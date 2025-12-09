#include <stdlib.h>
#include <unistd.h>
#include <stdio.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/epoll.h>
#include <errno.h>
#include <mqueue.h>
#include <string.h>
#include <stdbool.h>
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
  char c;
  while (c != '\0') {
    hash = ((hash << 5) + hash) + c;
  }
  return hash;
}


/**
   Concatenate a list of strings together and compute their hash
 */
unsigned long hash_array(int size, char** arr) {
  unsigned long hash = 5831;
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
    sprintf(fifo_path, "/tmp/%lx", cmd_hash);
    if (mkfifo(fifo_path, 0666) == -1) {
      if (errno == EEXIST) { // there was a hash collision 
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
                  char* mode,
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
  // Create the message: MODE;CWD;FIFO_PATH;rest;of;command...
  size_t initial_strlen = strlen(mode) + strlen(cwd) + strlen(fifopath) + 3; //3 separators 
  size_t bufsize = sizeof(char) * initial_strlen + 10;
  char * strbuf = (char *) malloc(bufsize);
  char padding = PADDING_CHAR;
  strcat(strbuf, mode);
  strncat(strbuf, &padding, sizeof(char));
  strcat(strbuf, cwd);
  strncat(strbuf, &padding, sizeof(char));
  strcat(strbuf, fifopath);
  strncat(strbuf, &padding, sizeof(char));
  size_t used_bytes = initial_strlen; 
  for (int i = 0; i < cmdlen; i++) {
    char *arg = cmdarr[i];
    size_t arglen = strlen(arg);
    used_bytes = used_bytes + arglen + 1; // add separator at the end 
    if (used_bytes >= bufsize) { // dynamic reallocation of the string
      strbuf = (char *)reallocarray(strbuf, bufsize * 2, sizeof(char));
    }
    strcat(strbuf, arg);
    strncat(strbuf, &padding, sizeof(char));
  }
  // turn the final separator into the null terminator and send the message
  strbuf[used_bytes-1] = '\0'; 
  if (mq_send(mqd, strbuf, used_bytes, 1) < 0) {
    return -1;
  }
  free(strbuf);
  return 0;
}

int main(int argc, char** argv) {
  char fifopath[32];
  char* mode = argv[1];
  char* cwd = argv[2];
  int cmdlen = argc - 3;
  char** cmdarr = argv + 3;
  // Setup return fifo
  if (make_unique_fifo(cmdlen, cmdarr, fifopath) < 0){
    perror("Error making return fifo");
    return 1;
  }
  // Submit the command to the clustcc MPI daemon
  if (send_task_msg(mode, cwd, fifopath, cmdlen, cmdarr) < 0) {
    perror("Error sending message");
    unlink(fifopath);
    return 1;
  }
  int fifo_fd = open(fifopath, O_RDONLY);
  // Read the return code
  char ret_code[1];
  int bytes_read = read(fifo_fd, ret_code, sizeof(char));
  if (bytes_read != sizeof(char)) {
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
