package ar.edu.itba.ss;

import java.util.ArrayList;
import java.util.List;
import java.util.Random;

public class Main {

    public static void main(String[] args) {
        for (String arg : args) {
            String[] parts = arg.split("=");
            if (parts.length != 2) continue; // ignora mal formateados

            String key = parts[0].toUpperCase();
            String value = parts[1];

            try {
                switch (key) {
                    case "BIG_RADIUS":
                        Parameters.BIG_RADIUS = Double.parseDouble(value);
                        break;
                    case "SMALL_RADIUS":
                        Parameters.SMALL_RADIUS = Double.parseDouble(value);
                        break;
                    case "PARTICLE_DEFAULT_RADIUS":
                        Parameters.PARTICLE_DEFAULT_RADIUS = Double.parseDouble(value);
                        break;
                    case "SPEED":
                        Parameters.SPEED = Double.parseDouble(value);
                        break;
                    case "DEFAULT_MASS":
                        Parameters.DEFAULT_MASS = Double.parseDouble(value);
                        break;
                    case "PARTICLE_COUNT":
                        Parameters.PARTICLE_COUNT = Integer.parseInt(value);
                        break;
                    default:
                        System.out.println("Parámetro desconocido: " + key);
                }
            } catch (NumberFormatException e) {
                System.err.println("Valor inválido para " + key + ": " + value);
            }
        }

        List<Particle> particles = new ArrayList<>();
        Random rand = new Random();
        Double minDistance = Parameters.PARTICLE_DEFAULT_RADIUS * 2;

        for (int i = 0; i < Parameters.PARTICLE_COUNT; i++) {
            double x = 0, y = 0;
            boolean valid = false;

            while (!valid) {
                valid = true;

                double radius = rand.nextDouble() * (Parameters.BIG_RADIUS - Parameters.SMALL_RADIUS) + Parameters.SMALL_RADIUS;
                double anglePos = rand.nextDouble() * 2 * Math.PI;
                x = radius * Math.cos(anglePos);
                y = radius * Math.sin(anglePos);

                for (Particle p : particles) {
                    double dx = x - p.x;
                    double dy = y - p.y;
                    double distSq = dx * dx + dy * dy;

                    if (distSq < minDistance * minDistance) {
                        valid = false;
                        break;
                    }
                }
            }

            double angle = rand.nextDouble() * 2 * Math.PI;
            double speed = Parameters.SPEED;
            double vx = speed * Math.cos(angle);
            double vy = speed * Math.sin(angle);
            particles.add(new Particle(x, y, vx, vy));
        }
        Simulation sim = new Simulation(particles, "results");
        sim.simulate(10.0, 0.1);
    }

}
