

from ast import literal_eval

from kivy.app import App
from kivy.clock import Clock
from kivy.app import Widget
from kivy.vector import Vector

import config
import utils
from network import Network as Network
from players.local import Local


class Game(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.network = Network()
        self.player = Local()
        self.player_paddle_mapping = {self.network.id: self.network.i}
        # When a paddle is not mapped to a player, then the paddle serves as barrier for its side
        self.paddles = [
            self.ids.paddle_left,
            self.ids.paddle_right,
            self.ids.paddle_top,
            self.ids.paddle_bottom
        ]

    def restart(self):
        for player_id, paddle_i in self.player_paddle_mapping.items():
            paddle = self.paddles[paddle_i]
            paddle.size = (config.paddle_height, config.paddle_height)
            if paddle.move_x:
                paddle.width = config.paddle_width
            if paddle.move_y:
                paddle.height = config.paddle_width

        self.ids.ball.reset((self.center_x, self.center_y+10))

    def update(self):
        updates = self.network.send(
            f"{self.network.id}:{self.player.target}"
        )
        updates, *news = updates.split('&')
        for new in news:
            id, i = new.split(':')
            self.player_paddle_mapping[id] = int(i)
            Clock.schedule_once(lambda dt: self.restart(), 5)
        for update in updates.split('|'):
            id, pos = update.split(':')
            pos = literal_eval(pos)
            i = self.player_paddle_mapping[id]
            paddle = self.paddles[i]
            paddle.move(pos)

        paddle_lines = [
            (
                (self.paddles[0].right, self.paddles[0].y),
                (self.paddles[0].right, self.paddles[0].top),
            ),
            (
                (self.paddles[1].x, self.paddles[1].y),
                (self.paddles[1].x, self.paddles[1].top),
            ),
            (
                (self.paddles[2].x, self.paddles[2].y),
                (self.paddles[2].right, self.paddles[2].y),
            ),
            (
                (self.paddles[3].x, self.paddles[3].top),
                (self.paddles[3].right, self.paddles[3].top),
            ),
        ]
        self.ids.ball.move(paddle_lines)

        if not self.collide_widget(self.ids.ball):
            self.restart()



class Paddle(Widget):
    def move(self, pos):
        x, y = pos
        if self.move_x:
            self.center_x = x
        if self.move_y:
            self.center_y = y


class Ball(Widget):
    velocity_x = 0
    velocity_y = 0
    mod = 1.

    @property
    def radius(self):
        assert self.width == self.height
        return self.width / 2

    def reset(self, pos=(0, 0)):
        self.center = pos
        self.velocity_x = 1
        self.velocity_y = 1
        self.mod = 1.

    def move(self, colliders):
        rem_vel_x = self.velocity_x
        rem_vel_y = self.velocity_y
        while rem_vel_x or rem_vel_y:  # while the ball can still move
            target_pos = Vector(rem_vel_x, rem_vel_y) + self.center
            for collider in colliders:
                point1, point2 = collider
                bounce_pos = utils.find_intersection(*self.center, *target_pos, *point1, *point2)
                if bounce_pos is None:
                    continue  # Will never collide unless angle changes
                distance_bounce = utils.distance(*self.center, *bounce_pos) - self.radius
                distance_target = utils.distance(*self.center, *target_pos)
                if distance_bounce > distance_target:
                    continue  # Did not collide yet
                if not utils.is_between(*collider, bounce_pos):
                    continue # Moves past collider
                break
            else:  # Did not collide with any collider -> free to move
                self.center_x += rem_vel_x * self.mod
                self.center_y += rem_vel_y * self.mod
                break
            dist_x = utils.to_zero(bounce_pos[0] - self.center_x, rem_vel_x)
            dist_y = utils.to_zero(bounce_pos[1] - self.center_y, rem_vel_y)
            rem_vel_x -= dist_x
            rem_vel_y -= dist_y
            if collider[0][0] == collider[1][0]:  # collider is vertical
                dist_x = -dist_x
                rem_vel_x = -rem_vel_x
                self.velocity_x = -self.velocity_x
            elif collider[0][1] == collider[1][1]:  # collider is horizontal
                dist_y = -dist_y
                rem_vel_y = -rem_vel_y
                self.velocity_y = -self.velocity_y
            else:
                raise ValueError("Collider", collider, "has to be a straight line")
            self.center_x += dist_x * self.mod
            self.center_y += dist_y * self.mod
            self.mod += .1


class PongApp(App):
    FPS = 60

    def build(self):
        game = Game()
        game.restart()
        Clock.schedule_interval(lambda dt: game.update(), 1./self.FPS)
        return game


if __name__ == '__main__':
    PongApp().run()