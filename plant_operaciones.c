/***********************************************
 *       MOLDE GENERAL PARA LABORATORIOS
 *   CPU-bound, I/O-bound, Hilos y Procesos
 *
 *   Cambia solo:
 *     - leer_csv() si cambia el archivo
 *     - analisis_cpu() si cambia el análisis
 *     - analisis_io() si cambias el archivo de lectura
 ***********************************************/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>
#include <time.h>
#include <unistd.h>
#include <sys/wait.h>

#define MAX_FILAS 2000
#define MAX_COLUMNAS 40
#define TOTAL_REP 1000

double datos[MAX_FILAS][MAX_COLUMNAS];
int filas = 0, columnas = 0;

/*************** 1. TIEMPO (NO CAMBIA) ************************/

double tiempo() {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + ts.tv_nsec / 1e9;
}

/*************** 2. LECTURA CSV (CAMBIA SI EL FORMATO CAMBIA) ********/

void leer_csv(char *nombre) {
    FILE *f = fopen(nombre, "r");
    if (!f) { printf("No se puede abrir archivo\n"); exit(1); }

    char linea[500];
    fgets(linea, sizeof(linea), f); // saltar cabecera si hay

    while (fgets(linea, sizeof(linea), f)) {
        char *tok = strtok(linea, ",");
        int col = 0;

        while (tok != NULL) {
            datos[filas][col++] = atof(tok);
            tok = strtok(NULL, ",");
        }

        columnas = col;
        filas++;
    }
    fclose(f);
}

/*************** 3. ANALISIS CPU (ESTA PARTE CAMBIA) ********/

void analisis_cpu() {

    /***** Ejemplo: análisis por columnas (MODIFICA AQUÍ) **/

    for (int c = 0; c < columnas; c++) {
        // reemplazar por tu mean/min/max/moda o nueva métrica
        // ejemplo:
        // double promedio = calcular_promedio_columna(c);
    }

    /***** Ejemplo: análisis por filas **/

    for (int i = 0; i < filas; i++) {
        // ejemplo:
        // double x = procesar_fila(i);
    }
}

/*************** 4. CPU SECUENCIAL (NO CAMBIA) ********/

void cpu_secuencial() {
    double inicio = tiempo();
    for (int i = 0; i < TOTAL_REP; i++)
        analisis_cpu();
    printf("CPU secuencial: %.6f\n", tiempo() - inicio);
}

/*************** 5. CPU CONCURRENTE (NO CAMBIA) ********/

void *trabajo_hilo(void *arg) {
    int reps = *((int *)arg);
    for (int r = 0; r < reps; r++)
        analisis_cpu();
    return NULL;
}

void cpu_concurrente(int nh) {
    pthread_t h[nh];
    int reps = TOTAL_REP / nh;

    double inicio = tiempo();
    for (int i = 0; i < nh; i++)
        pthread_create(&h[i], NULL, trabajo_hilo, &reps);

    for (int i = 0; i < nh; i++)
        pthread_join(h[i], NULL);

    printf("CPU concurrente (%02d hilos): %.6f\n", nh, tiempo() - inicio);
}

/*************** 6. CPU PARALELA (NO CAMBIA) ********/

void cpu_paralela(int np) {
    int reps = TOTAL_REP / np;
    double inicio = tiempo();

    for (int p = 0; p < np; p++) {
        if (fork() == 0) {
            for (int i = 0; i < reps; i++)
                analisis_cpu();
            exit(0);
        }
    }
    for (int p = 0; p < np; p++)
        wait(NULL);

    printf("CPU paralela (%02d procesos): %.6f\n", np, tiempo() - inicio);
}

/*************** 7. I/O BOUND (LEAN ARCHIVOS) ********/

void analisis_io() {

    // ejemplo I/O: lectura de archivo
    FILE *f = fopen("archivo.txt", "r");
    if (!f) return;

    char buffer[300];
    while (fgets(buffer, sizeof(buffer), f)) {}
    fclose(f);
}

void io_secuencial() {
    double inicio = tiempo();
    for (int i = 0; i < TOTAL_REP; i++)
        analisis_io();
    printf("IO secuencial: %.6f\n", tiempo() - inicio);
}

void *hilo_io(void *arg) {
    int reps = *((int*)arg);
    for (int i = 0; i < reps; i++)
        analisis_io();
    return NULL;
}

void io_concurrente(int nh) {
    pthread_t h[nh];
    int reps = TOTAL_REP / nh;

    double inicio = tiempo();
    for (int i = 0; i < nh; i++)
        pthread_create(&h[i], NULL, hilo_io, &reps);

    for (int i = 0; i < nh; i++)
        pthread_join(h[i], NULL);

    printf("IO concurrente (%02d hilos): %.6f\n", nh, tiempo() - inicio);
}

void io_paralela(int np) {
    int reps = TOTAL_REP / np;
    double inicio = tiempo();

    for (int p = 0; p < np; p++) {
        if (fork() == 0) {
            for (int i = 0; i < reps; i++)
                analisis_io();
            exit(0);
        }
    }
    for (int p = 0; p < np; p++)
        wait(NULL);

    printf("IO paralela (%02d procesos): %.6f\n", np, tiempo() - inicio);
}

/*************** 8. MAIN (PUEDES CAMBIAR SOLO EL ARCHIVO CSV) ********/

int main() {

    leer_csv("archivo.csv");
    printf("Filas: %d  Columnas: %d\n", filas, columnas);

    printf("\n=== CPU BOUND ===\n");
    cpu_secuencial();
    cpu_concurrente(4);
    cpu_paralela(4);

    printf("\n=== IO BOUND ===\n");
    io_secuencial();
    io_concurrente(4);
    io_paralela(4);

    return 0;
}
