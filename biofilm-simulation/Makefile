JAVAC=javac
JAVA=java
BIN_DIR=bin
MAIN_CLASS=UI

SRC_FILES=structuralPrototype/src/main/java/BacteriaCell.java \
	structuralPrototype/src/main/java/DataWriter.java \
	structuralPrototype/src/main/java/EPSParticle.java \
	structuralPrototype/src/main/java/EventCheckTask.java \
	structuralPrototype/src/main/java/ForceCalculationTask.java \
	structuralPrototype/src/main/java/ForceCalculator.java \
	structuralPrototype/src/main/java/GridCell.java \
	structuralPrototype/src/main/java/MultiThreadedSimulation.java \
	structuralPrototype/src/main/java/NutrientField.java \
	structuralPrototype/src/main/java/Particle.java \
	structuralPrototype/src/main/java/ParticleEvent.java \
	structuralPrototype/src/main/java/ParticleUpdateTask.java \
	structuralPrototype/src/main/java/SimulationConfig.java \
	structuralPrototype/src/main/java/SpatialGrid.java \
	structuralPrototype/src/main/java/UI.java \
	structuralPrototype/src/main/java/Vector2D.java \


all: compile

compile:
	@echo "Compiling Java source files..."
	@mkdir -p $(BIN_DIR)
	$(JAVAC) -d $(BIN_DIR) $(SRC_FILES)
	@echo "Compilation complete.."

run: compile
	@echo "Running Java UI..."
	$(JAVA) -cp $(BIN_DIR) $(MAIN_CLASS)

clean:
	@echo "Cleaning compiled files..."
	rm -rf $(BIN_DIR)
	@echo "Clean complete."