#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>
#include <time.h>
#include <unistd.h>
#include <sys/wait.h>

#define MAX_ALUMNOS 1000
#define N_LABS 8
#define TOTAL_REP 10000

double obtener_tiempo_real() {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec + (double)ts.tv_nsec / 1000000000.0;
}

double mean(double datos[], int n) {
    double suma = 0;
    for (int i = 0; i < n; i++)
        suma += datos[i];
    return suma / n;
}

double min(double datos[], int n) {
    double menor = datos[0];
    for (int i = 1; i < n; i++)
        if (datos[i] < menor) menor = datos[i];
    return menor;
}

double max(double datos[], int n) {
    double mayor = datos[0];
    for (int i = 1; i < n; i++)
        if (datos[i] > mayor) mayor = datos[i];
    return mayor;
}

double moda(double datos[], int n) {
    double modaValor = datos[0];
    int maxReps = 0;

    for (int i = 0; i < n; i++) {
        int reps = 0;
        for (int j = 0; j < n; j++)
            if (datos[i] == datos[j]) reps++;
        if (reps > maxReps) {
            maxReps = reps;
            modaValor = datos[i];
        }
    }
    return modaValor;
}

double nota_final(double labs[], int nLabs, double ex1, double ex2) {
    double promedioLabs = mean(labs, nLabs);
    return (6 * promedioLabs + 2 * ex1 + 2 * ex2) / 10.0;
}

double labs_arr[MAX_ALUMNOS][N_LABS];
double ex1_arr[MAX_ALUMNOS];
double ex2_arr[MAX_ALUMNOS];
int total_alumnos = 0;

void procesar_todos() {
    for (int i = 0; i < total_alumnos; i++) {
        double p  = mean(labs_arr[i], N_LABS);
        double mn = min(labs_arr[i], N_LABS);
        double mx = max(labs_arr[i], N_LABS);
        double mo = moda(labs_arr[i], N_LABS);
        double nf = nota_final(labs_arr[i], N_LABS, ex1_arr[i], ex2_arr[i]);
    }
}

void ejecucion_secuencial() {
    double inicio = obtener_tiempo_real();

    for (int r = 0; r < TOTAL_REP; r++)
        procesar_todos();

    double fin = obtener_tiempo_real();
    printf("\nTiempo de ejecución secuencial: %.6f segundos\n", fin - inicio);
}

void *trabajo_hilo(void *arg) {
    int reps = *((int*)arg);
    for (int r = 0; r < reps; r++)
        procesar_todos();
    return NULL;
}

void ejecucion_concurrente(int n_hilos) {
    pthread_t hilos[n_hilos];
    int reps_por_hilo = TOTAL_REP / n_hilos;

    double inicio = obtener_tiempo_real();

    for (int i = 0; i < n_hilos; i++)
        pthread_create(&hilos[i], NULL, trabajo_hilo, &reps_por_hilo);

    for (int i = 0; i < n_hilos; i++)
        pthread_join(hilos[i], NULL);

    double fin = obtener_tiempo_real();

    printf("Tiempo de ejecución concurrente con %d hilos: %.6f segundos\n",n_hilos, fin - inicio);
}

void ejecucion_paralela(int n_procesos) {
    int reps_por_proceso = TOTAL_REP / n_procesos;

    double inicio = obtener_tiempo_real();

    for (int p = 0; p < n_procesos; p++) {
        pid_t pid = fork();
        if (pid == 0) {
            for (int r = 0; r < reps_por_proceso; r++)
                procesar_todos();
            exit(0);
        }
    }

    for (int p = 0; p < n_procesos; p++)
        wait(NULL);

    double fin = obtener_tiempo_real();

    printf("Tiempo de ejecución paralela con %d procesos: %.6f segundos\n",n_procesos, fin - inicio);
}

void tarea_io() {
    FILE *f = fopen("notas_alumnos.csv", "r");
    if (!f) return;

    char buffer[300];
    while (fgets(buffer, sizeof(buffer), f)) { }

    fclose(f);
}

void io_secuencial() {
    double inicio = obtener_tiempo_real();

    for (int i = 0; i < TOTAL_REP; i++)
        tarea_io();

    double fin = obtener_tiempo_real();
    printf("\nI/O secuencial: %.6f segundos\n", fin - inicio);
}

void *trabajo_io_hilo(void *arg) {
    int reps = *((int*)arg);
    for (int i = 0; i < reps; i++)
        tarea_io();
    return NULL;
}

void io_concurrente(int n_hilos) {
    pthread_t h[n_hilos];
    int reps_por_hilo = TOTAL_REP / n_hilos;

    double inicio = obtener_tiempo_real();

    for (int i = 0; i < n_hilos; i++)
        pthread_create(&h[i], NULL, trabajo_io_hilo, &reps_por_hilo);

    for (int i = 0; i < n_hilos; i++)
        pthread_join(h[i], NULL);

    double fin = obtener_tiempo_real();

    printf("I/O concurrente con %d hilos: %.6f segundos\n",n_hilos, fin - inicio);
}

void io_paralela(int n_procesos) {
    int reps_por_proceso = TOTAL_REP / n_procesos;

    double inicio = obtener_tiempo_real();

    for (int p = 0; p < n_procesos; p++) {
        pid_t pid = fork();
        if (pid == 0) {
            for (int i = 0; i < reps_por_proceso; i++)
                tarea_io();
            exit(0);
        }
    }

    for (int p = 0; p < n_procesos; p++)
        wait(NULL);

    double fin = obtener_tiempo_real();

    printf("I/O paralela con %d procesos: %.6f segundos\n",n_procesos, fin - inicio);
}

int main() {

    FILE *file = fopen("notas_alumnos.csv", "r");
    if (!file) {
        printf("Error al abrir notas_alumnos.csv\n");
        return 1;
    }

    char linea[300];
    fgets(linea, sizeof(linea), file);

    while (fgets(linea, sizeof(linea), file)) {
        strtok(linea, ",");
        for (int i = 0; i < N_LABS; i++)
            labs_arr[total_alumnos][i] = atof(strtok(NULL, ","));
        ex1_arr[total_alumnos] = atof(strtok(NULL, ","));
        ex2_arr[total_alumnos] = atof(strtok(NULL, ","));
        total_alumnos++;
    }

    fclose(file);

    printf("Total alumnos cargados: %d\n\n", total_alumnos);

    printf("=== CPU BOUND ===\n");
    ejecucion_secuencial();

    for (int w = 2; w <= 40; w += 1) {
        ejecucion_concurrente(w);
    }

    for (int w = 2; w <= 40; w += 1) {
        ejecucion_paralela(w);
    }

    printf("\n=== I/O BOUND ===\n");
    io_secuencial();

    for (int w = 2; w <= 40; w += 1) {
        io_concurrente(w);
    }

    for (int w = 2; w <= 40; w += 1) {
        io_paralela(w);
    }

    return 0;
}
