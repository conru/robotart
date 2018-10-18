#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h> 

#include "bot.cpp"

void error(const char *msg)
{
  perror(msg);
  exit(0);
}

int main(int argc, char *argv[])
{
  PainterBot paintbot("localhost", 9999);
  paintbot.set_debug(1);

  Paint paint[3];
  paint[0].set_location_up(100, 50, 5); // x, y, z (above paint) in cm
  paint[0].set_location_down(100, 50, 10); // x, y, z (dipped in paint) in cm
  paint[0].set_color(220,20,50); // b, g, r
  paint[1].set_location_up(100, 100, 5); // x, y, z (above paint) in cm
  paint[1].set_location_down(100, 100, 10); // x, y, z (dipped in paint) in cm
  paint[1].set_color(90,220,50); // b, g, r
  paint[2].set_location_up(100, 150, 5); // x, y, z (above paint) in cm
  paint[2].set_location_down(100, 150, 10); // x, y, z (dipped in paint) in cm
  paint[2].set_color(20,120,250); // b, g, r

  paintbot.set_canvas_location(200, 50, .5);
  paintbot.set_canvas_dimensions(400, 300); // mm
  paintbot.open_draw_simulator();
  for (int i=0; i<3; i++) { paintbot.add_simulate_paint_location(paint[i]); }

  paintbot.set_max_speed(500); // mm/sec
  paintbot.set_speed(300); // mm/sec
  paintbot.set_pen_radius(8); // mm

  for (int i=0; i<3; i++) {
    paintbot.set_paint(paint[i]);
    paintbot.get_paint();
    paintbot.go_to_canvas_xy(10 + 30 * i,10 + 50 * i);
    paintbot.pen_down();
    paintbot.pause(30); // ms
    paintbot.go_to_canvas_xy(50 + 30 * i,10 + 50 * i);
    paintbot.go_to_canvas_xy(50 + 30 * i,50 + 50 * i);
    paintbot.go_to_canvas_xy(10 + 30 * i,50 + 50 * i);
    paintbot.go_to_canvas_xy(10 + 30 * i,10 + 50 * i);
    paintbot.pen_up();
  }

  paintbot.go_to_z(30);
  paintbot.go_to_xyz(100, 100, 30);
}
