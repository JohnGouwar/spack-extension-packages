#include <errno.h>
#include <fcntl.h>
#include <linux/limits.h>
#include <mqueue.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>
#include <sys/uio.h>
#ifndef MQ_NAME
  #define MQ_NAME "/spacktracemq"
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

int open_unique_shm_fd(int cmd_len, char** cmd, char* shm_name) {
  unsigned long cmd_hash = hash_array(cmd_len, cmd);
  bool unique = false;
  while (true) {
    sprintf(shm_name, "%lx_%d", cmd_hash, getpid());
    int shm_fd = shm_open(shm_name, O_CREAT | O_RDWR | O_EXCL, 0666);
    if (shm_fd < 0) {
      if (errno == EEXIST) {
        cmd_hash++;
      }
      else {
        perror("Attempting to open shared memory segment caused an error");
        return -1;
      }
    }
    else {
      return shm_fd;
    }
  };
  
}


int main(int argc, char** argv) {
  char shm_name[PATH_MAX];
  char wd[PATH_MAX];
  if (getcwd(wd, sizeof(wd)) < 0){
    perror("Failed to get working directory");
    return -1;
  }
  char padding[2] = {PADDING_CHAR, '\0'};
  char* spec_hash = argv[1];
  int cmd_len = argc - 2;
  char** cmd = argv + 2;
  mqd_t mqd = mq_open(MQ_NAME, O_RDWR);
  if (mqd < 0) {
    return -1;
  }
  int shm_fd = open_unique_shm_fd(cmd_len, cmd, shm_name);
  int iov_tot_len = argc*2 - 1;
  struct iovec iov[iov_tot_len];
  iov[0].iov_base = spec_hash;
  iov[0].iov_len = strlen(spec_hash);
  iov[1].iov_base = padding;
  iov[1].iov_len = 1;
  iov[2].iov_base = wd;
  iov[2].iov_len = (strlen(wd));
  iov[3].iov_base = padding;
  iov[3].iov_len = 1;
  for (int i = 0; i < (2*cmd_len - 1); i++) {
    if (i % 2 == 0) {
      iov[i+4].iov_base = cmd[i/2];
      iov[i+4].iov_len = strlen(cmd[i/2]);
    }
    else {
      iov[i+4].iov_base = padding;
      iov[i+4].iov_len = 1;
    }
  }
  size_t total_message_size = 0;
  for (int i = 0; i < iov_tot_len; i++){
    total_message_size += iov[i].iov_len;
  }
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
    perror("Failed to send message to mq");
    return -1;
  }
  munmap(shm_base, total_message_size);
  close(shm_fd);
  close(mqd);
  execv(cmd[0], cmd);
}
