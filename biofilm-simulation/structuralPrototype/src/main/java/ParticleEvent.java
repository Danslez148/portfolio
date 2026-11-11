
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;
import java.io.*;
// Event system for thread communication
class ParticleEvent {
    enum Type { DIVISION, EPS_SECRETION }
    
    private final Type type;
    private final BacteriaCell bacterium;
    
    public ParticleEvent(Type type, BacteriaCell bacterium) {
        this.type = type;
        this.bacterium = bacterium;
    }
    
    public Type getType() { return type; }
    public BacteriaCell getBacterium() { return bacterium; }
}
