# Software Ch3at - implementación independiente

El repositorio de **Software Ch3at** se creó como copia de Glizzy. No se ha modificado el original.

- App iOS: nombre, icono, textos, redes y paleta morada.
- Supabase NUEVO: https://jtifsqolnkxrououonjs.supabase.co
- Claves de activación: `SOFTCH3AT-...`
- Web única: `admin/index.html` (Archivos y Keys son pestañas de una sola web).
- SQL completo: `supabase/setup_softch3at.sql`, generado desde el setup completo original.
- IPA: workflow GitHub Actions, sin firma (para distribución, hay que firmarla).

## Orden de uso

1. GitHub Actions -> `Software Ch3at · Preparar, SQL, IPA y panel` -> Run workflow.
2. Esperar la ejecución de `Preparar identidad y SQL`. El workflow hace commit de los archivos de marca.
3. Descargar artefacto `Software-Ch3at-SQL-Completo`, extraer `setup_softch3at.sql`.
4. En el Supabase **nuevo**, SQL Editor -> New query -> pegar y Run. No usar en Glizzy.
5. Supabase Authentication -> Users: crear un usuario con `softwareapp98@gmail.com` si no existe;
   reejecutar el SQL para insertar automáticamente a este usuario en `license_admins`.
6. Entrar al panel con ese usuario Auth (no con las credenciales de la cuenta de dashboard).
7. Descargar el artefacto `Software-Ch3at-Admin-Panel` para web.
8. Descargar IPA de la ejecución si compiló. Archivo sin firma, requiere firma para instalar.

### Aviso de acceso

Si Supabase muestra `You do not have access to this project`, corrige acceso/cuenta
antes de ejecutar SQL. La publishable key es pública y NO concede permisos de administrador.

### Precauciones

- El `CFBundleIdentifier` / `PRODUCT_BUNDLE_IDENTIFIER` se conservan por compatibilidad técnica
  con la app base. Si quieres instalar Glizzy y Software Ch3at a la vez, será
  necesaria una segunda revisión del identificador y una prueba de compatibilidad.
- No se cambian el algoritmo de sincronización, los módulos de parchado, ni
  los archivos binarios de los parches.
- El bucket y las keys se aíslan en Supabase nuevo.
- Las redes antiguas ajenas a Software Ch3at deben revisarse antes de publicar:
  solo se actualizan TikTok y Discord que el propietario autorizó.
- Algunos mensajes internos (nombres técnicos de clases o rutas) siguen manteniendo
  nombres históricos por compatibilidad; NO se muestran como nueva marca.
