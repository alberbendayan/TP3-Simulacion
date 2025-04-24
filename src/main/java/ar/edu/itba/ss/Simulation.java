package ar.edu.itba.ss;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.text.DecimalFormat;
import java.text.DecimalFormatSymbols;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;
import java.util.Locale;
import java.util.PriorityQueue;

public class Simulation {

    private final double EPSILON = 1e-8;

    private final DecimalFormat df = new DecimalFormat("00.0000", new DecimalFormatSymbols(Locale.US));
    private final PriorityQueue<Event> pq = new PriorityQueue<>();
    private final String resultsPath;
    private final List<Particle> particles;

    private double t = 0.0;

    public Simulation(List<Particle> particles, String resultsPath) {
        this.particles = particles;
        this.resultsPath = String.format(Locale.US, "%s/%s", resultsPath, new SimpleDateFormat("yyyy-MM-dd-HH-mm-ss").format(new Date()));

        File dir = new File(this.resultsPath);
        if (!dir.exists() && !dir.mkdirs()) {
            System.err.println("Error al crear el directorio de resultados: " + resultsPath);
            System.exit(1);
        }

        saveState(0.0);  // Guardar el estado inicial
        saveConfig();  // Guardar la configuración
    }

    public void simulate(double limit) {
        t = 0.0;

        for (Particle p : particles) {
            predict(p, limit);
        }

        while (!pq.isEmpty()) {
            Event e = pq.poll();
            if (!e.isValid())
                continue;

            double dt = e.getTime() - t;
            for (Particle p : particles)
                p.move(dt);

            t = e.getTime();

            if (e.getA() != null && e.getB() != null)
                e.getA().bounceOff(e.getB());
            else if (e.getA() != null && e.getB() == null)
                e.getA().bounceOffCircularWall();  // Rebote contra la pared
            else if (e.getA() == null && e.getB() != null)
                e.getB().bounceOffObstacle();  // Rebote contra obstáculo

            saveState(t);  // Guardar el estado de la simulación

            // Predecir los siguientes eventos de colisión
            if (e.getA() != null) predict(e.getA(), limit);
            if (e.getB() != null) predict(e.getB(), limit);
        }
    }

    private void predict(Particle p, double limit) {
        double tWall = timeToCircularWallCollision(p);
        if (tWall > EPSILON && t + tWall < limit)
            pq.add(new Event(t + tWall, p, null));

        // No falta el else?
        if (Parameters.OBSTACLE_MASS == 0) {
            double tObstacle = timeToObstacleCollision(p);
            if (tObstacle > EPSILON && t + tObstacle < limit)
                pq.add(new Event(t + tObstacle, null, p));
        }

        for (Particle other : particles) {
            if (other == p) continue;
            double dt = timeToOtherParticle(p, other);
            if (t + dt < limit && dt > EPSILON)
                pq.add(new Event(t + dt, p, other));
        }
    }

    private double timeToOtherParticle(Particle a, Particle b) {
        if (a == b) return Double.POSITIVE_INFINITY;

        double dx = b.x - a.x;
        double dy = b.y - a.y;
        double dvx = b.vx - a.vx;
        double dvy = b.vy - a.vy;
        double dvdr = dx * dvx + dy * dvy;

        if (dvdr >= 0) return Double.POSITIVE_INFINITY; // se alejan

        double dvdv = dvx * dvx + dvy * dvy;
        double drdr = dx * dx + dy * dy;
        double sigma = a.radius + b.radius;
        double d = (dvdr * dvdr) - dvdv * (drdr - sigma * sigma);

        if (d < 0) return Double.POSITIVE_INFINITY; // no colisionan

        return -(dvdr + Math.sqrt(d)) / dvdv;
    }

    private double timeToCircularWallCollision(Particle p) {
        // Coordenadas del centro de la pared (asumiendo que está en (0,0))
        double x0 = p.x;
        double y0 = p.y;

        // Velocidad de la partícula
        double vx = p.vx;
        double vy = p.vy;

        // Radio de la pared (suponiendo que el radio de la pared es R)
        double R = Parameters.BIG_RADIUS;  // Esto es solo un ejemplo, usa el valor real de tu pared

        // Coeficientes de la ecuación cuadrática
        double A = vx * vx + vy * vy;
        double B = 2 * (x0 * vx + y0 * vy);
        double effectiveRadius = R - p.radius;
        double C = x0 * x0 + y0 * y0 - effectiveRadius * effectiveRadius;

        // Discriminante
        double discriminant = B * B - 4 * A * C;

        // Si el discriminante es negativo, no hay colisión
        if (discriminant < 0) {
            return Double.POSITIVE_INFINITY;  // No hay colisión
        }

        // Calculamos el tiempo de colisión
        double t1 = (-B + Math.sqrt(discriminant)) / (2 * A);
        double t2 = (-B - Math.sqrt(discriminant)) / (2 * A);

        // El tiempo válido será el menor t positivo
        if (t1 >= EPSILON && t2 >= EPSILON) {
            return Math.min(t1, t2);
        } else if (t1 >= EPSILON) {
            return t1;
        } else if (t2 >= EPSILON) {
            return t2;
        } else {
            return Double.POSITIVE_INFINITY;  // No hay colisión en el futuro
        }
    }

    private double timeToObstacleCollision(Particle p) {
        // Centro del obstáculo en (0, 0), radio pequeño
        double R = Parameters.SMALL_RADIUS;

        double x0 = p.x;
        double y0 = p.y;
        double vx = p.vx;
        double vy = p.vy;
        double effectiveRadius = R + p.radius;

        double A = vx * vx + vy * vy;
        double B = 2 * (x0 * vx + y0 * vy);
        double C = x0 * x0 + y0 * y0 - effectiveRadius * effectiveRadius;

        double discriminant = B * B - 4 * A * C;
        if (discriminant < 0)
            return Double.POSITIVE_INFINITY;

        double sqrtD = Math.sqrt(discriminant);
        double t1 = (-B + sqrtD) / (2 * A);
        double t2 = (-B - sqrtD) / (2 * A);

        if (t1 >= EPSILON && t2 >= EPSILON)
            return Math.min(t1, t2);
        else if (t1 >= EPSILON)
            return t1;
        else if (t2 >= EPSILON)
            return t2;
        else
            return Double.POSITIVE_INFINITY;
    }

    private void saveState(double time) {
        // Guardar dentro de carpeta 'snapshots' dentro de resultsPath
        File snapshotsDir = new File(resultsPath, "snapshots");
        if (!snapshotsDir.exists() && !snapshotsDir.mkdirs()) {
            System.err.println("Error al crear la carpeta de snapshots: " + snapshotsDir.getPath());
            System.exit(1);
        }

        String fileName = String.format(Locale.US, "%s/snapshot-%s.txt", snapshotsDir.getPath(), df.format(time));

        try (BufferedWriter writer = new BufferedWriter(new FileWriter(fileName))) {
            for (Particle p : particles)
                writer.write(String.format(Locale.US, "%.5f %.5f %.5f %.5f %.5f\n",
                        p.x, p.y, p.vx, p.vy, p.radius));
        } catch (IOException e) {
            System.err.println("Error al guardar snapshot: " + e.getMessage());
            System.exit(1);
        }
    }

    private void saveConfig() {
        // Guardar config.json directamente en resultsPath
        File dir = new File(resultsPath);
        if (!dir.exists() && !dir.mkdirs()) {
            System.err.println("Error al crear el directorio de resultados: " + resultsPath);
            System.exit(1);
        }

        File configFile = new File(dir, "config.json");

        try (BufferedWriter writer = new BufferedWriter(new FileWriter(configFile))) {
            writer.write("{\n");
            writer.write("  \"big_radius\": " + Parameters.BIG_RADIUS + ",\n");
            writer.write("  \"small_radius\": " + Parameters.SMALL_RADIUS + ",\n");
            writer.write("  \"particle_radius\": " + Parameters.PARTICLE_RADIUS + ",\n");
            writer.write("  \"speed\": " + Parameters.SPEED + ",\n");
            writer.write("  \"mass\": " + Parameters.MASS + ",\n");
            writer.write("  \"time_limit\": " + Parameters.TIME_LIMIT + ",\n");
            writer.write("  \"redraw_period\": " + Parameters.REDRAW_PERIOD + ",\n");
            writer.write("  \"obstacle_mass\": " + Parameters.OBSTACLE_MASS + ",\n");
            writer.write("  \"particle_count\": " + Parameters.PARTICLE_COUNT + "\n");
            writer.write("}\n");
        } catch (IOException e) {
            System.err.println("Error al guardar la configuración: " + e.getMessage());
        }
    }


}
