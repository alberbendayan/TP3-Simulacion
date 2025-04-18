package org.example;

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
            pq.add(new Event(redrawTime, null, null));
        }

        while (!pq.isEmpty()) {
            Event e = pq.poll();
            if (!e.isValid()) continue;

            double dt = e.time - t;
            for (Particle p : particles)
                p.move(dt);
            t = e.time;

            if (e.a != null && e.b != null) e.a.bounceOff(e.b);
            else if (e.a != null && e.b == null) e.a.bounceOffWall();
            else if (e.a == null && e.b != null) e.b.bounceOffWall();
            else if (e.a == null && e.b == null) {
                guardarEstado(t);
            }

            predict(e.a, limit);
            predict(e.b, limit);
        }
    }

    private void predict(Particle p, double limit) {
        // Eventos ignorados por ahora
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