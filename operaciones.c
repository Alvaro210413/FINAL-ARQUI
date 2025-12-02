#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>
#include <time.h>
#include <unistd.h>
#include <sys/wait.h>

#define MAX_ALUMNOS 1000
#define N_LABS 8
#define TOTAL_REP 1000
// gcc operaciones.c -o operaciones -pthread -lrt

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

void extraer_columna(double columna_temp[], int col_index, int es_lab) {
    if (es_lab) {
        for (int i = 0; i < total_alumnos; i++)
            columna_temp[i] = labs_arr[i][col_index];
    } else if (col_index == 0) {
        for (int i = 0; i < total_alumnos; i++)
            columna_temp[i] = ex1_arr[i];
    } else {
        for (int i = 0; i < total_alumnos; i++)
            columna_temp[i] = ex2_arr[i];
    }
}


void procesar_por_columna() {
    double columna_temp[MAX_ALUMNOS];

    for (int j = 0; j < N_LABS; j++) {
        extraer_columna(columna_temp, j, 1);
        
        double p  = mean(columna_temp, total_alumnos);
        double mn = min(columna_temp, total_alumnos);
        double mx = max(columna_temp, total_alumnos);
        double mo = moda(columna_temp, total_alumnos);
    }

    extraer_columna(columna_temp, 0, 0);
    double p1  = mean(columna_temp, total_alumnos);
    double mn1 = min(columna_temp, total_alumnos);
    double mx1 = max(columna_temp, total_alumnos);
    double mo1 = moda(columna_temp, total_alumnos);

    extraer_columna(columna_temp, 1, 0);
    double p2  = mean(columna_temp, total_alumnos);
    double mn2 = min(columna_temp, total_alumnos);
    double mx2 = max(columna_temp, total_alumnos);
    double mo2 = moda(columna_temp, total_alumnos);


    for (int i = 0; i < total_alumnos; i++) {
        double nf = nota_final(labs_arr[i], N_LABS, ex1_arr[i], ex2_arr[i]);
    }
}


void procesar_todos() {
    procesar_por_columna();
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

int main(){

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

------------------------------------------------------------------------------------------------------------------------------

#include <stdio.h>      // Funciones de entrada/salida: printf, fopen, fgets, fopen...
#include <stdlib.h>     // Conversión numérica, malloc, atof, exit
#include <string.h>     // Manejo de strings: strtok
#include <pthread.h>    // Biblioteca POSIX Threads → creación y manejo de hilos
#include <time.h>       // clock_gettime(), medición de tiempo de alta resolución
#include <unistd.h>     // fork(), sleep(), funciones del sistema Unix
#include <sys/wait.h>   // wait(), esperar procesos hijos

// ---------------------------- CONSTANTES DEL PROBLEMA ----------------------------

// Máximo de alumnos que soporta la memoria del programa
#define MAX_ALUMNOS 1000     

// Cada alumno tiene 8 notas de laboratorio
#define N_LABS 8              

// Número de repeticiones para evaluar rendimiento (CPU o I/O)
#define TOTAL_REP 1000        

// Compilación recomendada (porque se usa clock_monotonic y pthreads):
// gcc operaciones.c -o operaciones -pthread -lrt


// =================================================================================
// FUNCION DE TIEMPO (obtiene tiempo real de alta precisión)
// =================================================================================

// Utiliza CLOCK_MONOTONIC, que es estable frente a cambios manuales del reloj del SO.
double obtener_tiempo_real() {
    struct timespec ts;               // estructura con segundos y nanosegundos
    clock_gettime(CLOCK_MONOTONIC, &ts);  // obtiene el tiempo actual del sistema
    return (double)ts.tv_sec + (double)ts.tv_nsec / 1000000000.0;
}


// =================================================================================
// FUNCIONES ESTADÍSTICAS BÁSICAS (mean, min, max, moda)
// Cada una es CPU-bound porque operan con datos en memoria únicamente.
// =================================================================================

// Calcula el promedio de un arreglo de tamaño n
double mean(double datos[], int n) {
    double suma = 0;
    for (int i = 0; i < n; i++)
        suma += datos[i];            // suma todos los elementos
    return suma / n;                 // divide entre la cantidad
}

// Obtiene el valor mínimo del arreglo
double min(double datos[], int n) {
    double menor = datos[0];
    for (int i = 1; i < n; i++)
        if (datos[i] < menor)
            menor = datos[i];        // actualiza si encuentra un número menor
    return menor;
}

// Obtiene el valor máximo del arreglo
double max(double datos[], int n) {
    double mayor = datos[0];
    for (int i = 1; i < n; i++)
        if (datos[i] > mayor)
            mayor = datos[i];        // actualiza si encuentra un número mayor
    return mayor;
}

// Encuentra la moda (valor que más se repite) usando un algoritmo O(n^2)
// No es eficiente para n grande, pero n=8 aquí, así que es trivial.
double moda(double datos[], int n) {
    double modaValor = datos[0];
    int maxReps = 0;

    // compara cada elemento con todos los demás
    for (int i = 0; i < n; i++) {
        int reps = 0;

        for (int j = 0; j < n; j++)
            if (datos[i] == datos[j])
                reps++;             // cuenta cuántas veces aparece datos[i]

        if (reps > maxReps) {        // si aparece más veces que la moda actual
            maxReps = reps;
            modaValor = datos[i];
        }
    }
    return modaValor;
}


// Nota final ponderada: 60% laboratorios + 20% examen 1 + 20% examen 2
double nota_final(double labs[], int nLabs, double ex1, double ex2) {
    double promedioLabs = mean(labs, nLabs);
    return (6 * promedioLabs + 2 * ex1 + 2 * ex2) / 10.0;
}


// =================================================================================
// ARREGLOS GLOBALES QUE GUARDAN LAS NOTAS
// - labs_arr: notas de laboratorios por alumno
// - ex1_arr, ex2_arr: notas de exámenes
// - total_alumnos: contador dinámico de alumnos cargados desde CSV
// =================================================================================

double labs_arr[MAX_ALUMNOS][N_LABS];
double ex1_arr[MAX_ALUMNOS];
double ex2_arr[MAX_ALUMNOS];
int total_alumnos = 0;


// =================================================================================
// EXTRACCIÓN DE COLUMNAS (columna de laboratorio o examen)
// Se usa para procesar columnas completas (mean, min, max, moda)
// =================================================================================

void extraer_columna(double columna_temp[], int col_index, int es_lab) {

    // Si la columna es de labs (0–7)
    if (es_lab) {
        for (int i = 0; i < total_alumnos; i++)
            columna_temp[i] = labs_arr[i][col_index];

    // ex1_arr (col_index = 0) → primer examen
    } else if (col_index == 0) {
        for (int i = 0; i < total_alumnos; i++)
            columna_temp[i] = ex1_arr[i];

    // ex2_arr (col_index = 1) → segundo examen
    } else {
        for (int i = 0; i < total_alumnos; i++)
            columna_temp[i] = ex2_arr[i];
    }
}


// =================================================================================
// FUNCION PRINCIPAL DE PROCESAMIENTO CPU (usa mean, min, max, moda, nota_final)
// Este procesamiento NO imprime nada → rendimiento puro.
// =================================================================================

void procesar_por_columna() {
    double columna_temp[MAX_ALUMNOS];    // buffer temporal para análisis por columna

    // Procesar cada laboratorio como columna independiente
    for (int j = 0; j < N_LABS; j++) {

        extraer_columna(columna_temp, j, 1); // extrae columna j de labs

        double p  = mean(columna_temp, total_alumnos);
        double mn = min(columna_temp, total_alumnos);
        double mx = max(columna_temp, total_alumnos);
        double mo = moda(columna_temp, total_alumnos);

        // No se imprime nada para evitar alterar medición de CPU
    }

    // Procesar primera columna de exámenes
    extraer_columna(columna_temp, 0, 0);
    double p1  = mean(columna_temp, total_alumnos);
    double mn1 = min(columna_temp, total_alumnos);
    double mx1 = max(columna_temp, total_alumnos);
    double mo1 = moda(columna_temp, total_alumnos);

    // Procesar segunda columna de exámenes
    extraer_columna(columna_temp, 1, 0);
    double p2  = mean(columna_temp, total_alumnos);
    double mn2 = min(columna_temp, total_alumnos);
    double mx2 = max(columna_temp, total_alumnos);
    double mo2 = moda(columna_temp, total_alumnos);

    // Finalmente procesar la nota final de todos
    for (int i = 0; i < total_alumnos; i++) {
        double nf = nota_final(labs_arr[i], N_LABS, ex1_arr[i], ex2_arr[i]);
    }
}


// Wrapper de la función principal para mantener estructura clara
void procesar_todos() {
    procesar_por_columna();
}


// =================================================================================
// EJECUCIÓN CPU-BOUND SECUENCIAL (UN SOLO HILO)
// =================================================================================

void ejecucion_secuencial() {

    double inicio = obtener_tiempo_real();

    for (int r = 0; r < TOTAL_REP; r++)
        procesar_todos();

    double fin = obtener_tiempo_real();

    printf("\nTiempo de ejecución secuencial: %.6f segundos\n",
           fin - inicio);
}


// =================================================================================
// EJECUCIÓN CPU-BOUND CON HILOS (CONCURRENCIA)
// pthread_create crea varios hilos que COMPARTEN memoria.
// =================================================================================

// Cada hilo ejecuta parte del trabajo dividido
void *trabajo_hilo(void *arg) {
    int reps = *((int*)arg);         // número de repeticiones asignadas al hilo

    for (int r = 0; r < reps; r++)
        procesar_todos();

    return NULL;
}

// Crea n_hilos threads POSIX y distribuye la carga TOTAL_REP
void ejecucion_concurrente(int n_hilos) {

    pthread_t hilos[n_hilos];               // IDs de los hilos creados
    int reps_por_hilo = TOTAL_REP / n_hilos;

    double inicio = obtener_tiempo_real();

    // Crear hilos
    for (int i = 0; i < n_hilos; i++)
        pthread_create(&hilos[i], NULL, trabajo_hilo, &reps_por_hilo);

    // Esperar a que cada hilo termine (JOIN)
    // IMPORTANTE: esto asegura que el tiempo sea correcto
    for (int i = 0; i < n_hilos; i++)
        pthread_join(hilos[i], NULL);

    double fin = obtener_tiempo_real();

    printf("Tiempo de ejecución concurrente con %d hilos: %.6f segundos\n",
           n_hilos, fin - inicio);
}


// =================================================================================
// EJECUCIÓN CPU-BOUND PARALELA (PROCESOS → PARALELISMO REAL)
// Cada proceso creado con fork() tiene SU PROPIA COPIA DE MEMORIA.
// NO comparten variables globales.
// =================================================================================

void ejecucion_paralela(int n_procesos) {

    int reps_por_proceso = TOTAL_REP / n_procesos;

    double inicio = obtener_tiempo_real();

    for (int p = 0; p < n_procesos; p++) {

        pid_t pid = fork();       // Crea proceso hijo → MEMORY COPY

        if (pid == 0) {           // Código del proceso hijo

            for (int r = 0; r < reps_por_proceso; r++)
                procesar_todos();

            exit(0);              // Termina hijo y vuelve al SO
        }
    }

    // Proceso padre espera a los hijos → sincronización
    for (int p = 0; p < n_procesos; p++)
        wait(NULL);

    double fin = obtener_tiempo_real();

    printf("Tiempo de ejecución paralela con %d procesos: %.6f segundos\n",
           n_procesos, fin - inicio);
}


// =================================================================================
// TAREAS I/O-BOUND (lectura repetida de archivo CSV)
// =================================================================================

// Abre archivo, lo lee completamente línea por línea y lo cierra
void tarea_io() {

    FILE *f = fopen("notas_alumnos.csv", "r");
    if (!f) return;   // control de error

    char buffer[300];

    // Lectura del archivo completo (line by line)
    while (fgets(buffer, sizeof(buffer), f)) {}

    fclose(f);
}


// ----------------------- I/O secuencial -----------------------
void io_secuencial() {

    double inicio = obtener_tiempo_real();

    for (int i = 0; i < TOTAL_REP; i++)
        tarea_io();

    double fin = obtener_tiempo_real();

    printf("\nI/O secuencial: %.6f segundos\n", fin - inicio);
}


// ----------------------- I/O con hilos ------------------------
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

    printf("I/O concurrente con %d hilos: %.6f segundos\n",
           n_hilos, fin - inicio);
}


// ----------------------- I/O con procesos ------------------------
void io_paralela(int n_procesos) {

    int reps_por_proceso = TOTAL_REP / n_procesos;

    double inicio = obtener_tiempo_real();

    for (int p = 0; p < n_procesos; p++) {

        pid_t pid = fork();

        if (pid == 0) {  // proceso hijo
            for (int i = 0; i < reps_por_proceso; i++)
                tarea_io();
            exit(0);
        }
    }

    // el padre espera
    for (int p = 0; p < n_procesos; p++)
        wait(NULL);

    double fin = obtener_tiempo_real();

    printf("I/O paralela con %d procesos: %.6f segundos\n",
           n_procesos, fin - inicio);
}


// =================================================================================
//                                   MAIN
// =================================================================================

int main() {

    // Se abre archivo CSV que contiene notas de alumnos
    FILE *file = fopen("notas_alumnos.csv", "r");
    if (!file) {
        printf("Error al abrir notas_alumnos.csv\n");
        return 1;
    }

    char linea[300];

    // Leer primera línea (cabecera) y descartarla
    fgets(linea, sizeof(linea), file);

    // Leer línea por línea cada alumno
    while (fgets(linea, sizeof(linea), file)) {

        strtok(linea, ",");    // Ignorar primera columna (nombre/código)

        for (int i = 0; i < N_LABS; i++)
            labs_arr[total_alumnos][i] = atof(strtok(NULL, ","));

        ex1_arr[total_alumnos] = atof(strtok(NULL, ","));
        ex2_arr[total_alumnos] = atof(strtok(NULL, ","));

        total_alumnos++;
    }

    fclose(file);

    printf("Total alumnos cargados: %d\n\n", total_alumnos);


    // ============================= CPU BOUND =============================
    printf("=== CPU BOUND ===\n");
    ejecucion_secuencial();

    for (int w = 2; w <= 40; w++)
        ejecucion_concurrente(w);

    for (int w = 2; w <= 40; w++)
        ejecucion_paralela(w);


    // ============================= I/O BOUND =============================
    printf("\n=== I/O BOUND ===\n");
    io_secuencial();

    for (int w = 2; w <= 40; w++)
        io_concurrente(w);

    for (int w = 2; w <= 40; w++)
        io_paralela(w);

    return 0;
}

