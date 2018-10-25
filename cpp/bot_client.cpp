#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>

#include "bot.cpp"

// for this program to work, you must first run 'python3 bot_server.py' with localhost:9999

/* void error(const char *msg) {
  perror(msg);
  exit(0);
  } */

int main(int argc, char *argv[])
{
  PainterBot paintbot("localhost", 9999);
  paintbot.set_debug(1);  
  //paintbot.flip_xy(1);

  Paint paint[3];
  paint[0].set_location_up(100, 50, 20); // x, y, z (above paint) in cm
  paint[0].set_location_down(100, 50, 5); // x, y, z (dipped in paint) in cm
  paint[0].set_color(220,20,50); // b, g, r
  paint[1].set_location_up(100, 100, 20); // x, y, z (above paint) in cm
  paint[1].set_location_down(100, 100, 5); // x, y, z (dipped in paint) in cm
  paint[1].set_color(90,220,50); // b, g, r
  paint[2].set_location_up(100, 150, 20); // x, y, z (above paint) in cm
  paint[2].set_location_down(100, 150, 5); // x, y, z (dipped in paint) in cm
  paint[2].set_color(20,120,250); // b, g, r

  // 8.5x11" paper (portrait)
  //paintbot.set_canvas_location(216, 54, 1);
  //paintbot.set_canvas_dimensions(8.5 * 25.4, 11 * 25.4); // mm
  
  // 11x14" canvas board (landscape)
  paintbot.set_canvas_location(216, 54, 1);
  paintbot.set_canvas_dimensions(14 * 25.4, 11 * 25.4); // mm
  
  paintbot.open_draw_simulator();
  for (int i=0; i<3; i++) { paintbot.add_simulate_paint_location(paint[i]); }

  int fast = 50000;
  int slow = 3000;
  
  paintbot.set_pen_radius(8); // mm

  paintbot.drawCanvasOutline();
  
  // just test the is_idle() command
  //int idle = paintbot.is_idle();
  //printf("IS IDLE: %d\n", idle);

  for (int i=0; i<3; i++) {
    paintbot.set_paint(paint[i]);
    
    paintbot.set_speed(fast); // mm/sec
    paintbot.get_paint(300);
    paintbot.go_to_canvas_xy(10 + 30 * i,10 + 50 * i);
    paintbot.pen_down(2);
    paintbot.pause(30); // ms
    paintbot.go_to_canvas_xy(50 + 30 * i,10 + 50 * i);
    paintbot.go_to_canvas_xy(50 + 30 * i,50 + 50 * i);
    paintbot.go_to_canvas_xy(10 + 30 * i,50 + 50 * i);
    paintbot.go_to_canvas_xy(10 + 30 * i,10 + 50 * i);
    paintbot.pen_up(20);
  }

  paintbot.go_to_z(30);
  paintbot.go_to_xyz(100, 100, 30);
}
