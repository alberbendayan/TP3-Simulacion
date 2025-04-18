package org.example;

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
        // No implementado (placeholder para colisiones entre partículas)
    }

    public void bounceOffWall() {
        bounceIfWall(0.05); // radio del contenedor
    }

    public int getCollisionCount() {
        return collisionCount;
    }
}
