package ar.edu.itba.ss;

import java.util.Random;

public class Main {
    public static double SPEED = 0.1;
    public static double BIG_RADIUS = 0.05;
    public static double SMALL_RADIUS = 0.005;

    public static void main(String[] args) {
        Particle[] particles = new Particle[200];
        Random rand = new Random();

        for (int i = 0; i < particles.length; i++) {
            double angle = rand.nextDouble() * 2 * Math.PI;
            double speed = SPEED;
            double vx = speed * Math.cos(angle);
            double vy = speed * Math.sin(angle);

            double radius = rand.nextDouble() * (BIG_RADIUS - SMALL_RADIUS);
            double anglePos = rand.nextDouble() * 2 * Math.PI;
            double x = radius * Math.cos(anglePos);
            double y = radius * Math.sin(anglePos);

            particles[i] = new Particle(x, y, vx, vy);
        }
        try {
            new java.io.PrintWriter("output.txt").close();
        } catch (Exception e) {
            System.err.println("No se pudo limpiar output.txt");
        }

        Simulation sim = new Simulation(particles);
        sim.simulate(10.0,0.1);
    }
}
