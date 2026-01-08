#include <stdlib.h>
#include <sys/mman.h>
#include <unistd.h>
#include <stdio.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/epoll.h>
#include <sys/uio.h>
#include <errno.h>
#include <mqueue.h>
#include <string.h>
#include <stdbool.h>
#include <linux/limits.h>
#ifndef CLUSTCC_MQ
  #define CLUSTCC_MQ "/spackclustccmq"
#endif
#ifndef PADDING_CHAR
  #define PADDING_CHAR ';'
#endif

/**
   djb2 string hashing function
 */
unsigned long djb2_hash(char* str, unsigned long start_hash) {
  unsigned long hash = start_hash;
  unsigned char c;
  while ((c = *str++) != '\0') {
    hash = ((hash << 5) + hash) + c;
  }
  return hash;
}


/**
   Concatenate a list of strings together and compute their hash
 */
unsigned long hash_array(int size, char** arr) {
  unsigned long hash = 5381;
  for (int i = 0; i < size; i++){
    char* str = arr[i];
    hash = djb2_hash(str, hash);
  }
  return hash;
}


/**
   Makes a new fifo at a unique path derived from a hash of the command,
   incrementing in the case of collisions.

   Postcondition: If zero is returned, `fifo_path` is guaranteed to have the
   path to existing fifo
 */
int make_unique_fifo(int size, char** cmd_arr, char* fifo_path) {
  unsigned long cmd_hash = hash_array(size, cmd_arr);
  int unique = false;
  do {
    sprintf(fifo_path, "/tmp/%lx_%d", cmd_hash, getpid());
    if (mkfifo(fifo_path, 0666) == -1) {
      if (errno == EEXIST) { // there was a hash collision, this is super rare 
        cmd_hash++;
      }
      else {
        return -1;
      }
    }
    else {
      unique = true;
    }
  } while (!unique);
  return 0;
}


/**
   Send the message representing the compile task to the clustcc daemon
 */
int send_task_msg(
                  char* cwd,
                  char * fifopath,
                  int cmdlen,
                  char **cmdarr
                  ) {
  // Make sure we can open the message queue before allocating the string 
  mqd_t mqd = mq_open(CLUSTCC_MQ, O_RDWR);
  if (mqd < 0) {
    return -1;
  }
  char padding[2] = {PADDING_CHAR, '\0'};

  int iov_tot_len = ((cmdlen+2) * 2) - 1;
  struct iovec iov[iov_tot_len];
  iov[0].iov_base = cwd;
  iov[0].iov_len = strlen(cwd);
  iov[1].iov_base = padding;
  iov[1].iov_len = 1;
  iov[2].iov_base = fifopath;
  iov[2].iov_len = strlen(fifopath);
  iov[3].iov_base = padding;
  iov[3].iov_len = 1;
  for (int i = 0; i < (2 * cmdlen)-1; i++) {
    if (i % 2 == 0) {
      iov[i+4].iov_base = cmdarr[i / 2];
      iov[i+4].iov_len = strlen(cmdarr[i / 2]);
    }
    else {
      iov[i+4].iov_base = padding;
      iov[i+4].iov_len = 1;
    }
      
  }
  size_t total_message_size = 0;
  for (int i = 0; i < iov_tot_len; i++) {
    total_message_size += iov[i].iov_len;
  }
  char* shm_name = fifopath + 4; // trims /tmp
  int shm_fd = shm_open(shm_name, O_CREAT | O_RDWR, 0644);
  ftruncate(shm_fd, total_message_size);
  void* shm_base = mmap(NULL, total_message_size, PROT_READ | PROT_WRITE, MAP_SHARED, shm_fd, 0);
  void* curr_addr = shm_base;
  for (int i = 0; i < iov_tot_len; i++) {
    memcpy(curr_addr, iov[i].iov_base, iov[i].iov_len);
    curr_addr += iov[i].iov_len;
  }
  char msg[64];
  sprintf(msg, "%s%s%ld", shm_name, padding, total_message_size);
  if (mq_send(mqd, msg, strlen(msg)+1, 1) < 0) {
    return -1;
  }
  munmap(shm_base, total_message_size);
  close(shm_fd);
  return 0;
}

int main(int argc, char** argv) {
  char fifopath[32];
  char cwd[PATH_MAX];
  if (getcwd(cwd, sizeof(cwd)) == NULL) {
    perror("Failed to get cwd");
    return 1;
  }
  int cmdlen = argc - 1;
  char** cmdarr = argv + 1;
  // Setup return fifo
  if (make_unique_fifo(cmdlen, cmdarr, fifopath) < 0){
    perror("Error making return fifo");
    return 1;
  }
  // Submit the command to the clustcc MPI daemon
  int send_res = send_task_msg(cwd, fifopath, cmdlen, cmdarr);
  if (send_res < 0) {
    char err_buf[8192];
    perror("Wrapper error sending message");
    unlink(fifopath);
    return 1;
  }
  // Read the return code
  int fifo_fd = open(fifopath, O_RDONLY);
  char ret_code[1];
  int bytes_read = read(fifo_fd, ret_code, sizeof(char));
  if (bytes_read != sizeof(char)) {
    fprintf(stderr, "Bytes read: %d", bytes_read);
    perror("Error reading return code");
    close(fifo_fd);
    unlink(fifopath);
    return 1;
  }
  FILE *output_stream;
  if (ret_code[0] == 0) {
    output_stream = stdout;
  }
  else {
    output_stream = stderr;
  }
  char output_buffer[2048];
  // Stream output
  while (true) {
    bytes_read = read(fifo_fd, output_buffer, 2047);
    if (bytes_read == 0) { //
      close(fifo_fd);
      unlink(fifopath);
      return ret_code[0];
    }
    // Todo: Error handling
    output_buffer[bytes_read] = '\0';
    fputs(output_buffer, output_stream);
  }
}
