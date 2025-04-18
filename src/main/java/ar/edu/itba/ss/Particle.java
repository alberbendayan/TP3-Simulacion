package ar.edu.itba.ss;

public class Particle {
    public double x, y, vx, vy;
    public double radius = Parameters.PARTICLE_DEFAULT_RADIUS;
    public double mass = Parameters.DEFAULT_MASS;
    private int collisionCount = 0;

    public Particle(double x, double y, double vx, double vy) {
        this.x = x;
        this.y = y;
        this.vx = vx;
        this.vy = vy;
    }

    public Particle(double x, double y, double vx, double vy,double radius) {
        this.x = x;
        this.y = y;
        this.vx = vx;
        this.vy = vy;
        this.radius = radius;
    }


    public Particle(double x, double y, double vx, double vy,double radius,double mass) {
        this.x = x;
        this.y = y;
        this.vx = vx;
        this.vy = vy;
        this.radius = radius;
        this.mass = mass;
    }

    public void move(double dt) {
        x += vx * dt;
        y += vy * dt;
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
        double overlap = this.radius + other.radius - distance;

        if (overlap > 0) {
            // Normalizar el vector normal de colisión
            double nx = dx / distance;
            double ny = dy / distance;

            // Velocidad relativa en la dirección normal
            double dotProduct = (vx - other.vx) * nx + (vy - other.vy) * ny;

            // Solo procesar la colisión si las partículas se acercan
            if (dotProduct < 0) {
                // Calcular impulso considerando las masas
                double massFactor1 = (2 * other.mass) / (this.mass + other.mass);
                double massFactor2 = (2 * this.mass) / (this.mass + other.mass);

                // Actualizar velocidades según conservación de momento
                vx -= massFactor1 * dotProduct * nx;
                vy -= massFactor1 * dotProduct * ny;
                other.vx += massFactor2 * dotProduct * nx;
                other.vy += massFactor2 * dotProduct * ny;

                // Corregir solapamiento
                x -= overlap * nx / 2;
                y -= overlap * ny / 2;
                other.x += overlap * nx / 2;
                other.y += overlap * ny / 2;

                // Incrementar el contador de colisiones
                collisionCount++;
                other.collisionCount++;
            }
        }
    }


    public void bounceOffWall() {
        bounceIfWall(Parameters.BIG_RADIUS); // radio del contenedor
    }

    public int getCollisionCount() {
        return collisionCount;
    }
}
