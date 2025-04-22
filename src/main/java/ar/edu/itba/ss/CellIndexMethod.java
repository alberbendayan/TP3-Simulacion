package ar.edu.itba.ss;

import java.util.*;

class CellIndexMethod {

    private final int N, M;
    private final double L, Rc;
    private final List<Particle> particles;
    private final Map<Integer, Set<Particle>> grid;
    private final boolean periodic;

    public CellIndexMethod(int N, double L, int M, double Rc, boolean periodic, List<Particle> particles) {
        this.N = N;
        this.L = L;
        this.M = M;
        this.Rc = Rc;
        this.periodic = periodic;
        this.particles = particles;
        this.grid = new HashMap<>();

        initializeGrid();
        for (Particle p : particles) {
            addToGrid(p);
        }
    }

    public List<Particle> getParticles() {
        return particles;
    }

    public Set<Particle> findNeighbors(Particle p) {
        Set<Particle> neighbors = new HashSet<>();

        int cellIndex = getCellIndex(p.x, p.y);

        List<Particle> possibleNeighbors = getPossibleNeighbors(cellIndex);

        for (Particle neighbor : possibleNeighbors) {
            if (p.id != neighbor.id) {
                double distance;
                if (periodic) {
                    double dx = Math.abs(p.x - neighbor.x);
                    double dy = Math.abs(p.y - neighbor.y);
                    dx = Math.min(dx, L - dx);
                    dy = Math.min(dy, L - dy);
                    distance = Math.sqrt(dx * dx + dy * dy) - neighbor.radius;
                } else {
                    distance = p.distanceTo(neighbor);
                }
                if (distance < Rc) {
                    neighbors.add(neighbor);
                }
            }
        }
        return neighbors;
    }

    private List<Particle> getPossibleNeighbors(int cellIndex) {
        if (!grid.containsKey(cellIndex)) {
            return new ArrayList<>();
        }

        List<Particle> possibleNeighbors = new ArrayList<>(grid.get(cellIndex));
        int row = cellIndex / M;
        int col = cellIndex % M;
        int[] dx = {0, 1, 1, 0, -1, -1, -1, 0, 1};
        int[] dy = {0, 0, 1, 1, 1, 0, -1, -1, -1};

        for (int i = 0; i < dx.length; i++) {
            int newRow = row + dy[i];
            int newCol = col + dx[i];
            if (periodic) {
                newRow = (newRow + M) % M;
                newCol = (newCol + M) % M;
            }
            if (newRow >= 0 && newRow < M && newCol >= 0 && newCol < M) {
                int neighborIndex = newRow * M + newCol;
                possibleNeighbors.addAll(grid.get(neighborIndex));
            }
        }
        return possibleNeighbors;
    }

    private void initializeGrid() {
        for (int i = 0; i < M * M; i++) {
            grid.put(i, new HashSet<>());
        }
    }

    private int getCellIndex(double x, double y) {
        int row = (int) (y / (L / M));
        int col = (int) (x / (L / M));
        return row * M + col;
    }

    private void addToGrid(Particle p) {
        int index = getCellIndex(p.x, p.y);
        if (grid.containsKey(index)) {
            grid.get(index).add(p);
        }
    }

}
