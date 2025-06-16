import math
class Collidable():
    def handle_collisions(self, collidable_objects):
        damping_factor = 1

        for object in collidable_objects:
            if object is self:  # Don't collide with self
                continue

            dx = self.x - object.x
            dy = self.y - object.y
            distance = math.hypot(dx, dy)
            min_distance = self.radius + object.radius

            if distance < min_distance and distance != 0:
                # Collision detected!
                # 1. Resolve overlap (push them apart)
                overlap = min_distance - distance
                # Move both players away from each other proportionally to their masses, or simply half each
                # For simplicity, let's just push them equally apart along the collision normal
                # This prevents them from getting stuck, but can look a bit "jerky"
                correction_x = dx / distance * overlap * 0.5
                correction_y = dy / distance * overlap * 0.5

                self.x += correction_x
                self.y += correction_y
                object.x -= correction_x
                object.y -= correction_y

                # 2. Resolve velocities (elastic collision)
                # Unit normal vector
                nx = dx / distance
                ny = dy / distance

                # Unit tangent vector
                tx = -ny
                ty = nx

                # Project velocities onto the normal and tangent vectors
                # Player 1 (self)
                v1n = self.vel_x * nx + self.vel_y * ny
                v1t = self.vel_x * tx + self.vel_y * ty

                # Player 2 (other_player)
                v2n = object.vel_x * nx + object.vel_y * ny
                v2t = object.vel_x * tx + object.vel_y * ty

                m1 = self.mass
                m2 = object.mass

                v1n_final = (v1n * (m1 - m2) + 2 * m2 * v2n) / (m1 + m2)
                v2n_final = (v2n * (m2 - m1) + 2 * m1 * v1n) / (m1 + m2)

                # Convert scalar normal and tangent velocities back to vectors
                self.vel_x = v1n_final * nx + v1t * tx
                self.vel_y = v1n_final * ny + v1t * ty

                object.vel_x = v2n_final * nx + v2t * tx
                object.vel_y = v2n_final * ny + v2t * ty

                # Add a small damping to prevent infinite bouncing or
                # to simulate some energy loss (optional)
                self.vel_x *= damping_factor
                self.vel_y *= damping_factor
                object.vel_x *= damping_factor
                object.vel_y *= damping_factor
