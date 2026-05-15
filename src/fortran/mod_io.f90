!===============================================================================
! mod_io.f90
! Módulo de entrada/salida de datos
!
! Responsabilidad: Manejar toda la lectura de parámetros y escritura
! de resultados del sistema. Actúa como interfaz entre el motor
! numérico Fortran y el pipeline de visualización Python.
!
! Formatos de salida:
!   - CSV para compatibilidad directa con pandas/numpy
!   - Headers descriptivos para autodocumentación
!   - Nombres de archivo ordenados para ensamblado de video
!
! Autor: Proyecto Física II — Universidad Cooperativa de Colombia
!===============================================================================
module mod_io
    use mod_constants
    use mod_types
    implicit none

    ! Unidades de archivo (Fortran I/O units)
    integer, parameter :: UNIT_PARAMS  = 10
    integer, parameter :: UNIT_ENERGY  = 20
    integer, parameter :: UNIT_CONFIG  = 30
    integer, parameter :: UNIT_FINAL   = 40
    integer, parameter :: UNIT_INITIAL = 50

contains

    !===========================================================================
    ! Subrutina: read_parameters
    !
    ! Lee los parámetros de simulación desde archivo de texto.
    ! Formato: una variable por línea, valor seguido de comentario.
    !
    ! Archivo esperado: data/input/simulation_params.txt
    !
    ! Diseño defensivo: si el archivo no existe, usa valores default
    ! definidos en mod_constants.
    !===========================================================================
    subroutine read_parameters(param_file)
        character(len=*), intent(in) :: param_file
        integer  :: ios
        logical  :: file_exists

        ! Verificar existencia del archivo
        inquire(file=param_file, exist=file_exists)

        if (.not. file_exists) then
            write(*,'(A)') '  [WARNING] Archivo de parametros no encontrado.'
            write(*,'(A)') '  Usando valores por defecto.'
            return
        end if

        open(unit=UNIT_PARAMS, file=param_file, status='old', iostat=ios)

        if (ios /= 0) then
            write(*,'(A,I0)') '  [ERROR] No se pudo abrir archivo: iostat=', ios
            return
        end if

        ! Leer parámetros (formato: valor en cada línea)
        read(UNIT_PARAMS, *, iostat=ios) N_PARTICLES
        read(UNIT_PARAMS, *, iostat=ios) L_DOMAIN
        read(UNIT_PARAMS, *, iostat=ios) DELTA_MOVE
        read(UNIT_PARAMS, *, iostat=ios) MAX_ITER
        read(UNIT_PARAMS, *, iostat=ios) CHARGE_MODE
        read(UNIT_PARAMS, *, iostat=ios) SAVE_EVERY
        read(UNIT_PARAMS, *, iostat=ios) PRINT_EVERY
        read(UNIT_PARAMS, *, iostat=ios) SEED_VALUE

        close(UNIT_PARAMS)

        ! Validaciones físicas y numéricas
        if (N_PARTICLES < 2 .or. N_PARTICLES > MAX_PARTICLES) then
            write(*,'(A,I0,A,I0)') '  [ERROR] N_PARTICLES debe ser 2..', &
                MAX_PARTICLES, ', recibido: ', N_PARTICLES
            N_PARTICLES = 50
        end if

        if (L_DOMAIN <= 0.0_dp) then
            write(*,'(A)') '  [ERROR] L_DOMAIN debe ser > 0. Usando default.'
            L_DOMAIN = 10.0_dp
        end if

        if (DELTA_MOVE <= 0.0_dp) then
            write(*,'(A)') '  [ERROR] DELTA_MOVE debe ser > 0. Usando default.'
            DELTA_MOVE = 0.25_dp
        end if

        if (MAX_ITER < 1) then
            write(*,'(A)') '  [ERROR] MAX_ITER debe ser >= 1. Usando default.'
            MAX_ITER = 500000
        end if

        if (CHARGE_MODE /= 1 .and. CHARGE_MODE /= 2) then
            write(*,'(A)') '  [WARNING] CHARGE_MODE invalido. Usando 1.'
            CHARGE_MODE = 1
        end if

    end subroutine read_parameters

    !===========================================================================
    ! Subrutina: print_parameters
    !
    ! Imprime los parámetros de simulación actuales en pantalla.
    !===========================================================================
    subroutine print_parameters()

        write(*,'(A)')    '  =============================================='
        write(*,'(A)')    '  PARAMETROS DE SIMULACION'
        write(*,'(A)')    '  =============================================='
        write(*,'(A,I6)')       '  N particulas    = ', N_PARTICLES
        write(*,'(A,F8.2)')     '  L dominio       = ', L_DOMAIN
        write(*,'(A,F8.4)')     '  Delta movimiento= ', DELTA_MOVE
        write(*,'(A,I10)')      '  Max iteraciones = ', MAX_ITER
        write(*,'(A,I2)')       '  Modo de cargas  = ', CHARGE_MODE
        write(*,'(A,I6)')       '  Guardar cada    = ', SAVE_EVERY
        write(*,'(A,I6)')       '  Imprimir cada   = ', PRINT_EVERY
        write(*,'(A,I10)')      '  Semilla random   = ', SEED_VALUE
        write(*,'(A,ES10.2)')   '  Softening eps   = ', EPSILON_SOFT
        write(*,'(A)')    '  =============================================='

    end subroutine print_parameters

    !===========================================================================
    ! Subrutina: open_energy_log
    !
    ! Abre el archivo de registro de energía con header CSV.
    !===========================================================================
    subroutine open_energy_log(filename)
        character(len=*), intent(in) :: filename
        integer :: ios

        open(unit=UNIT_ENERGY, file=filename, status='replace', iostat=ios)

        if (ios /= 0) then
            write(*,'(A)') '  [ERROR] No se pudo crear archivo de energia.'
            stop 1
        end if

        ! Header CSV
        write(UNIT_ENERGY, '(A)') 'iteration,accepted_count,energy,acceptance_rate'

    end subroutine open_energy_log

    !===========================================================================
    ! Subrutina: write_energy_log
    !
    ! Escribe una línea en el registro de energía.
    !===========================================================================
    subroutine write_energy_log(iteration, accepted_count, energy, acceptance_rate)
        integer, intent(in)  :: iteration, accepted_count
        real(dp), intent(in) :: energy, acceptance_rate

        write(UNIT_ENERGY, '(I10,A,I10,A,ES20.12,A,F8.4)') &
            iteration, ',', accepted_count, ',', energy, ',', acceptance_rate

    end subroutine write_energy_log

    !===========================================================================
    ! Subrutina: close_energy_log
    !===========================================================================
    subroutine close_energy_log()
        close(UNIT_ENERGY)
    end subroutine close_energy_log

    !===========================================================================
    ! Subrutina: save_configuration
    !
    ! Guarda la configuración actual del sistema en un archivo CSV
    ! con nombre secuencial para ensamblado de video.
    !
    ! Formato: config_NNNNNN.csv
    !   Columnas: particle_id, x, y, charge
    !===========================================================================
    subroutine save_configuration(sys, config_number, directory)
        type(particle_system), intent(in) :: sys
        integer, intent(in) :: config_number
        character(len=*), intent(in) :: directory
        character(len=512) :: filename
        integer :: i, ios

        ! Nombre secuencial con zero-padding para orden correcto
        write(filename, '(A,A,I6.6,A)') trim(directory), '/config_', config_number, '.csv'

        open(unit=UNIT_CONFIG, file=filename, status='replace', iostat=ios)

        if (ios /= 0) then
            write(*,'(A,A)') '  [ERROR] No se pudo crear: ', trim(filename)
            return
        end if

        ! Header
        write(UNIT_CONFIG, '(A)') 'particle_id,x,y,charge'

        ! Datos de cada partícula
        do i = 1, sys%n
            write(UNIT_CONFIG, '(I6,A,ES18.10,A,ES18.10,A,F4.1)') &
                i, ',', sys%x(i), ',', sys%y(i), ',', sys%q(i)
        end do

        close(UNIT_CONFIG)

    end subroutine save_configuration

    !===========================================================================
    ! Subrutina: save_final_configuration
    !
    ! Guarda la configuración final con información adicional.
    !===========================================================================
    subroutine save_final_configuration(sys, filename)
        type(particle_system), intent(in) :: sys
        character(len=*), intent(in) :: filename
        integer :: i, ios

        open(unit=UNIT_FINAL, file=filename, status='replace', iostat=ios)

        if (ios /= 0) then
            write(*,'(A)') '  [ERROR] No se pudo crear archivo de config final.'
            return
        end if

        ! Header
        write(UNIT_FINAL, '(A)') 'particle_id,x,y,charge'

        do i = 1, sys%n
            write(UNIT_FINAL, '(I6,A,ES18.10,A,ES18.10,A,F4.1)') &
                i, ',', sys%x(i), ',', sys%y(i), ',', sys%q(i)
        end do

        close(UNIT_FINAL)

    end subroutine save_final_configuration

    !===========================================================================
    ! Subrutina: save_initial_configuration
    !
    ! Guarda la configuración inicial para comparación.
    !===========================================================================
    subroutine save_initial_configuration(sys, filename)
        type(particle_system), intent(in) :: sys
        character(len=*), intent(in) :: filename
        integer :: i, ios

        open(unit=UNIT_INITIAL, file=filename, status='replace', iostat=ios)

        if (ios /= 0) then
            write(*,'(A)') '  [ERROR] No se pudo crear config inicial.'
            return
        end if

        write(UNIT_INITIAL, '(A)') 'particle_id,x,y,charge'

        do i = 1, sys%n
            write(UNIT_INITIAL, '(I6,A,ES18.10,A,ES18.10,A,F4.1)') &
                i, ',', sys%x(i), ',', sys%y(i), ',', sys%q(i)
        end do

        close(UNIT_INITIAL)

    end subroutine save_initial_configuration

end module mod_io
