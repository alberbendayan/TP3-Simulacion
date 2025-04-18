package ar.edu.itba.ss;

import java.io.FileWriter;
import java.io.IOException;
import java.util.PriorityQueue;

public class Simulation {
    private final PriorityQueue<Event> pq = new PriorityQueue<>();
    private final Particle[] particles;
    private double t = 0.0;

    public Simulation(Particle[] particles) {
        this.particles = particles;
    }

    public void simulate(double limit) {
        for (double redrawTime = 0.1; redrawTime <= limit; redrawTime += 0.1) {
            pq.add(new Event(redrawTime, null, null));  // Evento para cada paso de simulación
        }

        while (!pq.isEmpty()) {
            Event e = pq.poll();
            if (!e.isValid()) continue;

            double dt = e.time - t;
            for (Particle p : particles) p.move(dt);
            t = e.time;

            if (e.a != null && e.b != null) {
                e.a.bounceOff(e.b);  // Colisión entre partículas
            } else if (e.a != null && e.b == null) {
                e.a.bounceOffWall();  // Rebote contra la pared
            } else if (e.a == null && e.b != null) {
                e.b.bounceOffWall();  // Rebote contra la pared
            } else if (e.a == null && e.b == null) {
                guardarEstado(t);  // Guardar el estado de la simulación
            }

            // Predecir los siguientes eventos de colisión
            for (Particle p : particles) {
                predict(p, limit);
            }
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
                double relVel = dx * dvx + dy * dvy;  // Producto escalar

                // Si las partículas se acercan, predice el evento de colisión
                if (relVel < 0 && dist < 2 * p.radius) {
                    double d = dx * dx + dy * dy;
                    double a = dvx * dvx + dvy * dvy;
                    double b = 2 * (dx * dvx + dy * dvy);
                    double c = d - 4 * p.radius * p.radius;
                    double discriminant = b * b - 4 * a * c;

                    if (discriminant >= 0) {
                        double sqrtDisc = Math.sqrt(discriminant);
                        double t1 = (-b - sqrtDisc) / (2 * a);
                        double t2 = (-b + sqrtDisc) / (2 * a);
                        double t = Math.min(t1, t2);

                        if (t > 0 && t < limit) {
                            pq.add(new Event(t + t, p, other));
                        }
                    }
                }
            }
        }
    }


    private void guardarEstado(double tiempo) {
        try (FileWriter writer = new FileWriter("output.txt", true)) {
            for (Particle p : particles) {
                writer.write(String.format("%.5f %.5f\n", p.x, p.y));
            }
            writer.write("---\n");
        } catch (IOException e) {
            System.err.println("Error al guardar snapshot: " + e.getMessage());
        }
    }
}