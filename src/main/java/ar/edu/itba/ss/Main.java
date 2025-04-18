package ar.edu.itba.ss;

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
                    default:
                        System.out.println("Parámetro desconocido: " + key);
                }
            } catch (NumberFormatException e) {
                System.err.println("Valor inválido para " + key + ": " + value);
            }
        }

        Particle[] particles = new Particle[200];
        Random rand = new Random();

        for (int i = 0; i < particles.length; i++) {
            double angle = rand.nextDouble() * 2 * Math.PI;
            double speed = Parameters.SPEED;
            double vx = speed * Math.cos(angle);
            double vy = speed * Math.sin(angle);

            double radius = rand.nextDouble() * (Parameters.BIG_RADIUS - Parameters.SMALL_RADIUS);
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
