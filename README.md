# GLOBAL IOS

Proyecto iOS y panel de administración NUEVOS, basados en el código de `app-software`, con backend independiente.

- Repo destino: **emmajestevex-ui/app-global**. Repo origen solo lectura: **emmajestevex-ui/app-software**.
- Nombre: **GLOBAL IOS**. Tema blanco/negro/gris. Sin redes sociales.
- Supabase destino: https://tqdbvswgpmtbfezwucli.supabase.co
- Key pública: `sb_publishable_dR7EYTs81scCKwgWNkwFug_2Y4scFhh` (NO es una clave de administrador).
- Prefijo licencias `GLOBALIOS-`. Bucket `globalios-content`.
- Una sola web admin/index.html, con pestañas de Archivos y Keys.
- SQL de instalación: `supabase/SETUP_GLOBAL_IOS_COMPLETO.sql`.
- SQL para asignar ADMIN: `supabase/ASIGNAR_ADMIN_GLOBAL_IOS.sql` (personalizar correo).
- Workflow: Actions > GLOBAL IOS - Migrar, SQL, Panel e IPA.

**Importante:** Clave, usuarios Auth, tablas, datos, Storage y panel deben pertenecer al **nuevo proyecto**. No copiamos datos de otras empresas. El SQL y la IPA aún necesitan pruebas reales.

El CFBundleIdentifier ahora es `com.globalios.client` para evitar colisiones de instalación con otras apps; verificar que las funciones del app base sigan funcionando en el dispositivo.

El logo proporcionado se parece al de Apple: para distribución comercial verifica tus derechos de uso de esa marca. Este proyecto NO es una aplicación oficial de Apple.
