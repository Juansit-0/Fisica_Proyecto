!===============================================================================
! main.f90
! Programa principal — Simulación de Cargas Eléctricas
!
! Pipeline de ejecución:
!   1. Leer parámetros de simulación
!   2. Inicializar sistema de partículas
!   3. Guardar configuración inicial
!   4. Ejecutar algoritmo de minimización
!   5. Guardar configuración final
!   6. Reportar estadísticas
!
! Uso:
!   $ ./electrostatic_sim
!
! Prerequisitos:
!   - Archivo data/input/simulation_params.txt
!   - Directorios data/output/ y data/output/configurations/
!
! Autor: Proyecto Física II — Universidad Cooperativa de Colombia
!===============================================================================
program electrostatic_simulation
    use mod_constants
    use mod_types
    use mod_energy
    use mod_io
    use mod_simulation
    implicit none

    ! Variables locales
    type(particle_system) :: sys
    real(dp) :: t_start, t_end

    ! =========================================================================
    ! Banner del programa
    ! =========================================================================
    write(*,'(A)') ''
    write(*,'(A)') '  ****************************************************'
    write(*,'(A)') '  *                                                  *'
    write(*,'(A)') '  *   SIMULACION DE CARGAS ELECTROSTATICAS           *'
    write(*,'(A)') '  *   Minimizacion de Energia Electrostatica         *'
    write(*,'(A)') '  *                                                  *'
    write(*,'(A)') '  *   Proyecto de Electricidad y Magnetismo          *'
    write(*,'(A)') '  *   Universidad Cooperativa de Colombia            *'
    write(*,'(A)') '  *   M.Sc. Alejandro Molina                        *'
    write(*,'(A)') '  *                                                  *'
    write(*,'(A)') '  *   Arquitectura: Fortran 90 + Python              *'
    write(*,'(A)') '  *                                                  *'
    write(*,'(A)') '  ****************************************************'
    write(*,'(A)') ''

    ! =========================================================================
    ! Fase 1: Lectura de parámetros
    ! =========================================================================
    write(*,'(A)') '  [1/5] Leyendo parametros de simulacion...'
    call read_parameters('data/input/simulation_params.txt')
    call print_parameters()

    ! =========================================================================
    ! Fase 2: Inicialización del sistema
    ! =========================================================================
    write(*,'(A)') '  [2/5] Inicializando sistema de particulas...'
    call initialize_system(sys)

    ! Calcular y reportar energía inicial
    sys%total_energy = compute_total_energy(sys)
    write(*,'(A,ES14.6)') '  Energia inicial calculada = ', sys%total_energy
    write(*,'(A,I4,A)')   '  Sistema inicializado con ', sys%n, ' particulas'

    ! =========================================================================
    ! Fase 3: Guardar configuración inicial
    ! =========================================================================
    write(*,'(A)') '  [3/5] Guardando configuracion inicial...'
    call save_initial_configuration(sys, 'data/output/initial_config.csv')

    ! =========================================================================
    ! Fase 4: Ejecutar simulación
    ! =========================================================================
    write(*,'(A)') '  [4/5] Ejecutando simulacion de minimizacion...'

    ! Abrir log de energía
    call open_energy_log('data/output/energy_log.csv')

    ! Medir tiempo de ejecución
    call cpu_time(t_start)

    ! Ejecutar algoritmo principal
    call run_simulation(sys)

    call cpu_time(t_end)

    ! Cerrar log de energía
    call close_energy_log()

    ! =========================================================================
    ! Fase 5: Guardar resultados finales
    ! =========================================================================
    write(*,'(A)') '  [5/5] Guardando configuracion final...'
    call save_final_configuration(sys, 'data/output/final_config.csv')

    ! =========================================================================
    ! Reporte de rendimiento
    ! =========================================================================
    write(*,'(A)')         ''
    write(*,'(A)')         '  =============================================='
    write(*,'(A)')         '  RENDIMIENTO'
    write(*,'(A)')         '  =============================================='
    write(*,'(A,F10.3,A)') '  Tiempo de ejecucion   = ', t_end - t_start, ' s'
    write(*,'(A,ES10.2,A)')'  Iteraciones/segundo   = ', &
        real(MAX_ITER, dp) / (t_end - t_start), ' iter/s'
    write(*,'(A)')         '  =============================================='
    write(*,'(A)')         ''
    write(*,'(A)') '  Simulacion completada exitosamente.'
    write(*,'(A)') '  Ejecute el pipeline Python para visualizacion:'
    write(*,'(A)') '    $ python3 src/python/run_visualization.py'
    write(*,'(A)') ''

end program electrostatic_simulation
