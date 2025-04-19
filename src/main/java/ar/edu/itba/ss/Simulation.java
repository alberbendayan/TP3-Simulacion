package ar.edu.itba.ss;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;
import java.util.PriorityQueue;

public class Simulation {

    private final PriorityQueue<Event> pq = new PriorityQueue<>();
    private final Particle[] particles;
    private final String resultsPath;

    private double t = 0.0;

    public Simulation(Particle[] particles, String resultsPath) {
        this.particles = particles;
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

        while (!pq.isEmpty()) {
            Event e = pq.poll();
            if (!e.isValid())
                continue;

            double dt = e.getTime() - t;
            for (Particle p : particles)
                p.move(dt);

            t = e.getTime();

            if (e.getA() != null && e.getB() != null)
                e.getA().bounceOff(e.getB());  // Colisión entre partículas
            else if (e.getA() != null && e.getB() == null)
                e.getA().bounceOffWall();  // Rebote contra la pared
            else if (e.getA() == null && e.getB() != null)
                e.getB().bounceOffWall();  // Rebote contra la pared
            else if (e.getA() == null && e.getA() == null)
                saveState(t);  // Guardar el estado de la simulación

            // Predecir los siguientes eventos de colisión
            for (Particle p : particles)
                predict(p, limit);
        }
    }


    private void predict(Particle p, double limit) {
        for (Particle other : particles) {
            if (p != other) {
                double dx = other.x - p.x;
                double dy = other.y - p.y;
                double dvx = other.vx - p.vx;
                double dvy = other.vy - p.vy;

                double dist = Math.sqrt(dx * dx + dy * dy);
                double relVel = dx * dvx + dy * dvy;

                /*
                 * - relVel < 0: Significa que las partículas se están acercando entre sí.
                 *     Un producto escalar negativo indica que los vectores tienen componentes en
                 *     direcciones opuestas.
                 * - dist < 2 * p.radius: Comprueba si la distancia entre partículas es menor que
                 *     la suma de sus diámetros.
                 */
                if (relVel < 0 && dist < other.radius + p.radius) {
                    double d = dx * dx + dy * dy;
                    double a = dvx * dvx + dvy * dvy;
                    double b = 2 * (dx * dvx + dy * dvy);
                    double c = d - 4 * p.radius * p.radius;
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

    private void saveState(double time) {
        String fileName = String.format(Locale.US, "%s/snapshot-%.2f.txt", resultsPath, time);

        try (BufferedWriter writer = new BufferedWriter(new FileWriter(fileName))) {
            for (Particle p : particles)
                writer.write(String.format("%.5f %.5f\n", p.x, p.y));
        } catch (IOException e) {
            System.err.println("Error al guardar snapshot: " + e.getMessage());
            System.exit(1);
        }
    }

}