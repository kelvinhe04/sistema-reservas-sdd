# Outcomes (ODD)

Estado: borrador del ciclo 1 (Product / Spec Lead). Los supuestos marcados con **[Supuesto]** deben ser validados por el grupo.

## Problema

Las reservas de canchas deportivas se coordinan por WhatsApp o por llamadas. Esto genera:

- cruces de horarios y dobles reservas de la misma cancha en la misma hora;
- dependencia del personal para responder, confirmar y anotar cada reserva;
- el cliente no sabe qué horarios están libres sin preguntar;
- el administrador no tiene una agenda única y confiable del día.

## Usuarios

| Usuario | Qué necesita |
|---|---|
| Jugador (cliente) | Ver horarios libres y reservar una cancha sin escribirle a nadie |
| Administrador de la cancha | Ver la agenda del día, gestionar canchas y bloquear horarios sin conflictos |

## Outcomes esperados

| ID | Resultado para el usuario | Cómo sabemos que se logró |
|---|---|---|
| O-01 | Nunca se confirman dos reservas para la misma cancha y franja | Cero dobles reservas, incluso con solicitudes simultáneas (prueba automatizada) |
| O-02 | El jugador encuentra un horario libre y reserva sin intervención del personal | Una reserva se completa en menos de 2 minutos y sin contactar a nadie |
| O-03 | El jugador puede consultar o cancelar su reserva por su cuenta | Con su código y teléfono ve su reserva y la cancela dentro de la ventana permitida |
| O-04 | El administrador tiene una agenda única y confiable | La agenda del día muestra todas las reservas, bloqueos y horarios libres por cancha |
| O-05 | Los horarios cancelados se vuelven a ofrecer de inmediato | Una franja cancelada aparece como disponible en la siguiente consulta |

## Fuera de alcance (v1)

- Pagos en línea.
- Cuentas de usuario con registro e inicio de sesión para jugadores.
- Notificaciones por correo, SMS o WhatsApp.
- Reservas recurrentes y torneos.

## Supuestos

- **[Supuesto]** El jugador se identifica solo con nombre y teléfono, sin cuenta.
- **[Supuesto]** Hay un único administrador que accede con una clave.
- **[Supuesto]** Una sola sede, con varias canchas.
- **[Supuesto]** El sistema es una aplicación web.
