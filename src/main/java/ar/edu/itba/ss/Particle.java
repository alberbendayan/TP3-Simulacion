package ar.edu.itba.ss;

public class Particle {
    public double x, y, vx, vy;
    public final double radius = 0.0005;
    public final double mass = 1.0;
    private int collisionCount = 0;

    public Particle(double x, double y, double vx, double vy) {
        this.x = x;
        this.y = y;
        this.vx = vx;
        this.vy = vy;
    }

    public void updatePosition(double dt) {
        x += vx * dt;
        y += vy * dt;
    }

    public void move(double dt) {
        updatePosition(dt);
    }

    public void bounceIfWall(double boundaryRadius) {
        double dist = Math.sqrt(x * x + y * y);
        if (dist + radius >= boundaryRadius) {
            double nx = x / dist;
            double ny = y / dist;
            double dot = vx * nx + vy * ny;
            vx -= 2 * dot * nx;
            vy -= 2 * dot * ny;
        }
    }

    public void bounceIfObstacle(double obstacleRadius) {
        double dist = Math.sqrt(x * x + y * y);
        if (dist <= obstacleRadius + radius) {
            double nx = x / dist;
            double ny = y / dist;
            double dot = vx * nx + vy * ny;
            vx -= 2 * dot * nx;
            vy -= 2 * dot * ny;
        }
    }

    public void bounceOff(Particle other) {
        double dx = other.x - this.x;
        double dy = other.y - this.y;
        double distance = Math.sqrt(dx * dx + dy * dy);
        double overlap = 2 * radius - distance;

        if (overlap > 0) {
            double nx = dx / distance;
            double ny = dy / distance;
            double dotProduct = (vx - other.vx) * nx + (vy - other.vy) * ny;

            // Reflexión en la dirección normal
            vx -= dotProduct * nx;
            vy -= dotProduct * ny;
            other.vx += dotProduct * nx;
            other.vy += dotProduct * ny;

            // Resolver el solapamiento (si es necesario)
            x -= overlap * nx / 2;
            y -= overlap * ny / 2;
            other.x += overlap * nx / 2;
            other.y += overlap * ny / 2;

            // Incrementar el contador de colisiones
            collisionCount++;
            other.collisionCount++;
        }
    }


    public void bounceOffWall() {
        bounceIfWall(0.05); // radio del contenedor
    }

    public int getCollisionCount() {
        return collisionCount;
    }
}
