package ar.edu.itba.ss;

public class Particle {

    public static int LAST_ID = 1;

    public final int id;
    public final double radius = Parameters.PARTICLE_DEFAULT_RADIUS;

    public double x, y;
    public double vx, vy;
    public double mass;
    private int collisionCount = 0;

    public Particle(double x, double y, double vx, double vy) {
        this.id = LAST_ID++;
        this.x = x;
        this.y = y;
        this.vx = vx;
        this.vy = vy;
        this.mass = Parameters.DEFAULT_MASS;
    }

    public void move(double dt) {
        x += vx * dt;
        y += vy * dt;
    }

    public void bounceOff(Particle that) {
        double dx = that.x - this.x;
        double dy = that.y - this.y;
        double dvx = that.vx - this.vx;
        double dvy = that.vy - this.vy;
        double dvdr = dx * dvx + dy * dvy;
        double dist = this.radius + that.radius;

        // magnitud del impulso
        double J = 2 * this.mass * that.mass * dvdr / ((this.mass + that.mass) * dist);
        double Jx = J * dx / dist;
        double Jy = J * dy / dist;

        this.vx += Jx / this.mass;
        this.vy += Jy / this.mass;
        that.vx -= Jx / that.mass;
        that.vy -= Jy / that.mass;

        this.collisionCount++;
        that.collisionCount++;
    }

    public void bounceOffCircularWall() {
        double dist = Math.sqrt(x * x + y * y);
        double nx = x / dist;
        double ny = y / dist;
        double dot = vx * nx + vy * ny;

        // Reflect velocity
        vx -= 2 * dot * nx;
        vy -= 2 * dot * ny;

        // Empujón pequeño para sacar la partícula del borde
        double EPSILON_DISPLACEMENT = 1e-6;
        x += vx * EPSILON_DISPLACEMENT;
        y += vy * EPSILON_DISPLACEMENT;

        collisionCount++;
    }

    public void bounceOffObstacle() {
        // Assuming obstacle is fixed at (0,0), same as bounceOffCircularWall
        bounceOffCircularWall();
    }

    public int getCollisionCount() {
        return collisionCount;
    }

    public double distanceTo(Particle other) {
        double dx = this.x - other.x;
        double dy = this.y - other.y;
        return Math.sqrt(dx * dx + dy * dy) - other.radius;
    }

}
