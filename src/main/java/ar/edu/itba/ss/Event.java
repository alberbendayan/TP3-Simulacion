package ar.edu.itba.ss;

public class Event implements Comparable<Event> {
    public final double time;
    public final Particle a, b;
    private final int countA, countB;

    public Event(double t, Particle a, Particle b) {
        this.time = t;
        this.a = a;
        this.b = b;
        this.countA = a != null ? a.getCollisionCount() : -1;
        this.countB = b != null ? b.getCollisionCount() : -1;
    }

    public boolean isValid() {
        return (a == null || a.getCollisionCount() == countA) &&
                (b == null || b.getCollisionCount() == countB);
    }

    @Override
    public int compareTo(Event that) {
        return Double.compare(this.time, that.time);
    }
}