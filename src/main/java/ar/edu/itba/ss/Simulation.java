package ar.edu.itba.ss;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.text.DecimalFormat;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;
import java.util.Locale;
import java.util.PriorityQueue;

public class Simulation {

    private final DecimalFormat df = new DecimalFormat("00.00");
    private final PriorityQueue<Event> pq = new PriorityQueue<>();
    private final String resultsPath;
    private final CellIndexMethod cim;

    private double t = 0.0;

    public Simulation(List<Particle> particles, String resultsPath) {
        // TODO: definir L, M y Rc y periodic
        this.cim = new CellIndexMethod(particles.size(), 1.0, 10, 0.1, false, particles);
        this.resultsPath = String.format(Locale.US, "%s/%s", resultsPath, new SimpleDateFormat("yyyy-MM-dd-HH-mm-ss").format(new Date()));

        File dir = new File(this.resultsPath);
        if (!dir.exists() && !dir.mkdirs()) {
            System.err.println("Error al crear el directorio de resultados: " + resultsPath);
            System.exit(1);
        }

        saveState(0.0);  // Guardar el estado inicial
    }

    public void simulate(double limit, double redrawPeriod) {
        t = 0.0;

        for (double redrawTime = redrawPeriod; redrawTime <= limit; redrawTime += redrawPeriod) {
            pq.add(new Event(redrawTime, null, null));  // Evento para cada paso de simulación
        }

        for (Particle p : cim.getParticles()) {
            predict(p, limit);
        }

        while (!pq.isEmpty()) {
            Event e = pq.poll();
            if (!e.isValid())
                continue;

            double dt = e.getTime() - t;
            for (Particle p : cim.getParticles())
                p.move(dt);

            t = e.getTime();

            if (e.getA() != null && e.getB() != null)
                e.getA().bounceOff(e.getB());  // Colisión entre partículas
            else if (e.getA() != null && e.getB() == null)
                e.getA().bounceOffCircularWall();  // Rebote contra la pared
            else if (e.getA() == null && e.getB() != null)
                e.getB().bounceOffObstacle();  // Rebote contra obstáculo
            else if (e.getA() == null && e.getB() == null)
                saveState(t);  // Guardar el estado de la simulación

            // Predecir los siguientes eventos de colisión
            if (e.getA() != null) predict(e.getA(), limit);
            if (e.getB() != null) predict(e.getB(), limit);
        }
    }

    private void predict(Particle p, double limit) {
        double tWall = timeToCircularWallCollision(p);
        if (tWall > 0 && t + tWall < limit)
            pq.add(new Event(t + tWall, p, null));

        double tObstacle = timeToObstacleCollision(p);
        if (tObstacle > 0 && t + tObstacle < limit)
            pq.add(new Event(t + tObstacle, null, p));

        for (Particle other : cim.findNeighbors(p)) {
            if (p != other) {
                double dx = other.x - p.x;
                double dy = other.y - p.y;
                double dvx = other.vx - p.vx;
                double dvy = other.vy - p.vy;

                double dist = Math.sqrt(dx * dx + dy * dy);
                double relVel = dx * dvx + dy * dvy;

                if (relVel < 0 && dist < other.radius + p.radius) {
                    double d = dx * dx + dy * dy;
                    double a = dvx * dvx + dvy * dvy;
                    double b = 2 * (dx * dvx + dy * dvy);
                    double c = d - (p.radius + other.radius) * (p.radius + other.radius);
                    double discriminant = b * b - 4 * a * c;

                    if (discriminant >= 0) {
                        double sqrtDisc = Math.sqrt(discriminant);
                        double t1 = (-b - sqrtDisc) / (2 * a);
                        double t2 = (-b + sqrtDisc) / (2 * a);
                        double timeCol = -1;

                        if (t1 >= 0 && t2 >= 0)
                            timeCol = Math.min(t1, t2);
                        else if (t1 >= 0)
                            timeCol = t1;
                        else if (t2 >= 0)
                            timeCol = t2;

                        if (timeCol > 0 && t + timeCol < limit)
                            pq.add(new Event(t + timeCol, p, other));
                    }
                }
            }
        }
    }

    private double timeToCircularWallCollision(Particle p) {
        double radius = 0.05; // L/2
        double px = p.x, py = p.y;
        double vx = p.vx, vy = p.vy;
        double pr = p.radius;

        double A = vx * vx + vy * vy;
        double B = 2 * (px * vx + py * vy);
        double C = px * px + py * py - (radius - pr) * (radius - pr);

        double discriminant = B * B - 4 * A * C;
        if (discriminant < 0) return -1;

        double sqrtD = Math.sqrt(discriminant);
        double t1 = (-B + sqrtD) / (2 * A);
        double t2 = (-B - sqrtD) / (2 * A);

        double t = (t1 > 0 && t2 > 0) ? Math.min(t1, t2) : (t1 > 0 ? t1 : t2);
        return t > 0 ? t : -1;
    }

    private double timeToObstacleCollision(Particle p) {
        double obstacleRadius = 0.005;
        double px = p.x, py = p.y;
        double vx = p.vx, vy = p.vy;
        double pr = p.radius;

        double A = vx * vx + vy * vy;
        double B = 2 * (px * vx + py * vy);
        double C = px * px + py * py - (obstacleRadius + pr) * (obstacleRadius + pr);

        double discriminant = B * B - 4 * A * C;
        if (discriminant < 0) return -1;

        double sqrtD = Math.sqrt(discriminant);
        double t1 = (-B + sqrtD) / (2 * A);
        double t2 = (-B - sqrtD) / (2 * A);

        double t = (t1 > 0 && t2 > 0) ? Math.min(t1, t2) : (t1 > 0 ? t1 : t2);
        return t > 0 ? t : -1;
    }

    private void saveState(double time) {
        String fileName = String.format(Locale.US, "%s/snapshot-%s.txt", resultsPath, df.format(time));

        try (BufferedWriter writer = new BufferedWriter(new FileWriter(fileName))) {
            for (Particle p : cim.getParticles())
                writer.write(String.format("%.5f %.5f\n", p.x, p.y));
        } catch (IOException e) {
            System.err.println("Error al guardar snapshot: " + e.getMessage());
            System.exit(1);
        }
    }

}
