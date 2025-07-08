SELECT id,
       fecha_operacion,
       concepto,
       fecha_valor,
       importe,
       saldo,
       referencia_1,
       referencia_2
FROM public.gastos_2025
LIMIT 1000;

SELECT * 
from public.gastos_2025
WHERE fecha_operacion >= '2025-03-01' AND fecha_operacion < '2025-03-31';

Create OR REPLACE VIEW public.vw_gastos2025_enero AS
SELECT *
FROM public.gastos_2025
WHERE fecha_operacion >= '2025-01-01' AND fecha_operacion < '2025-02-01';

SELECT * FROM public.vw_gastos2025_enero
order by fecha_operacion asc;

CREATE OR REPLACE VIEW public.vw_gastos2025_febrero AS
SELECT *
FROM public.gastos_2025
WHERE fecha_operacion >= '2025-02-01' AND fecha_operacion < '2025-03-01';   

CREATE OR REPLACE VIEW public.vw_gastos2025_marzo AS
SELECT *
FROM public.gastos_2025
WHERE fecha_operacion >= '2025-03-01' AND fecha_operacion < '2025-04-01';

CREATE OR REPLACE VIEW public.vw_gastos2025_abril AS
SELECT *
FROM public.gastos_2025
WHERE fecha_operacion >= '2025-04-01' AND fecha_operacion < '2025-05-01';

CREATE OR REPLACE VIEW public.vw_gastos2025_mayo AS
SELECT *
FROM public.gastos_2025
WHERE fecha_operacion >= '2025-05-01' AND fecha_operacion < '2025-06-01';

SELECT *
    FROM public.vw_gastos2025_mayo
    ORDER BY fecha_operacion ASC;