package org.example;

import java.util.Random;

public class Main {
    public static void main(String[] args) {
        Particle[] particles = new Particle[200];
        Random rand = new Random();

        for (int i = 0; i < particles.length; i++) {
            double angle = rand.nextDouble() * 2 * Math.PI;
            double speed = 1.0;
            double vx = speed * Math.cos(angle);
            double vy = speed * Math.sin(angle);

            double radius = rand.nextDouble() * (0.05 - 0.0005);
            double anglePos = rand.nextDouble() * 2 * Math.PI;
            double x = radius * Math.cos(anglePos);
            double y = radius * Math.sin(anglePos);

            particles[i] = new Particle(x, y, vx, vy);
        }

        // limpiar archivo antes de escribir
        try {
            new java.io.PrintWriter("output.txt").close();
        } catch (Exception e) {
            System.err.println("No se pudo limpiar output.txt");
        }

        Simulation sim = new Simulation(particles);
        sim.simulate(10.0); // 10 segundos
    }
}
