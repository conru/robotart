#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h> 

// Class to send commands to robot via socket connection

class Bot {
protected:
  int sockfd, portno, n;
  struct sockaddr_in serv_addr;
  struct hostent *server;
  const char *host_name;
  int port_number;
  int debug;
public:
  int to_point() { return 3; }

  int connect_to_socket() {
    sockfd = socket(AF_INET, SOCK_STREAM, 0);

    if (sockfd < 0)  {
      perror("ERROR opening socket");
      return 0;
    }

    server = gethostbyname(host_name);

    bzero((char *) &serv_addr, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    bcopy((char *)server->h_addr, 
	  (char *)&serv_addr.sin_addr.s_addr,
	  server->h_length);
    serv_addr.sin_port = htons(port_number);

    if (::connect(sockfd,(struct sockaddr *) &serv_addr,sizeof(serv_addr)) < 0) {
      perror("ERROR connecting");
      return 0;
    }
    return 1;
  }

  int send_to_socket(const char *text) {
    int ok = connect_to_socket();
    if (debug) printf("OK:%d\n", ok);
    if (!ok) { return 0; }

    if (sockfd < 0)  { 
      printf("No socket connection\n");
      return 0; 
    }
    ok = write(sockfd, text, strlen(text));
    close(sockfd);
    return ok;
  }

  int go_to_xyz(float x, float y, float z) {
    char buf[50];
    sprintf(buf,"GO X%f Y%f Z%f",x,y,z);
    if (debug) printf("SENDING %s\n", buf);
    return send_to_socket(buf);
  }

  int go_to_xy(float x, float y) {
    return go_to_xyz(x,y,-1);
  }

  int go_to_z(float z) {
    return go_to_xyz(-1, -1, z);
  }

  int set_speed(float cm_per_sec) {
    char buf[50];
    sprintf(buf,"SPEED V%f",cm_per_sec);
    if (debug) printf("SENDING %s\n", buf);
    return send_to_socket(buf);
  }

  void set_debug(int d) { debug = d; }

  Bot(const char *host, int portno) {
    host_name = host;
    port_number = portno;
    sockfd = -1;
    debug = 0;
  }
};


void error(const char *msg)
{
  perror(msg);
  exit(0);
}

int main(int argc, char *argv[])
{
  Bot mybot("localhost", 9999);
  mybot.set_debug(1);

  mybot.set_speed(50); // cm/sec

  for (int i=0; i<5; i++) {
    mybot.go_to_xyz(10,10,3);
    mybot.go_to_xyz(50,10,4);
    mybot.go_to_xyz(50,50,5);
    mybot.go_to_xyz(10,50,6);
  }

  mybot.go_to_z(3);

}
