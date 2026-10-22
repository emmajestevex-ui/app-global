#!/usr/bin/env python3
"""Branding-only migration for the copied GLLYZI-APP repository.

Input: existing repo with source, admin/index.html, admin/app.js, supabase/setup_all.sql.
Output: separate Software Ch3at branding and a *complete* SQL file generated
        from the exact source SQL. Does not execute SQL or deploy it.

The patch is idempotent. It deliberately DOES NOT change patch engines, binary
payloads, synchronisation algorithms, or the iOS bundle identifier (which the
base patcher may depend on for compatibility). The latter needs device testing.
"""
from __future__ import annotations
import argparse
import json
import re
import shutil
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT_REF = "jtifsqolnkxrououonjs"
NEW_URL = f"https://{PROJECT_REF}.supabase.co"
NEW_PUBLIC_KEY = "sb_publishable_vVlLdGyUErtzRfSyPU426g_WqVACybG"
OLD_URL = "https://zffwtixmbuctinffojwe.supabase.co"
OLD_PUBLIC_KEY = "sb_publishable_6xRmOLD0Cw4Dtwn460l_Zw_Y7khT6wA"
BRAND = "Software Ch3at"
PREFIX = "SOFTCH3AT"
ADMIN_EMAIL = "softwareapp98@gmail.com"
TIKTOK = "https://www.tiktok.com/@soyenyercitord?_r=1&_t=ZS-9AkGglyDhcy"
DISCORD = "https://discord.gg/6SScyh8yC"
CHANGED = []


def read(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Archivo necesario ausente: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def write(path: Path, data: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists() or path.read_text(encoding="utf-8") != data:
        path.write_text(data, encoding="utf-8")
        CHANGED.append(str(path.relative_to(ROOT)))


def replace_base(text: str) -> str:
    # No old project's URL, publishable key, name, licence prefix, or namespace.
    text = text.replace(OLD_URL, NEW_URL).replace(OLD_PUBLIC_KEY, NEW_PUBLIC_KEY)
    text = text.replace("Glizzy Net", BRAND).replace("GLIZZY NET", BRAND.upper())
    text = text.replace("gllyzi app", BRAND).replace("GLLYZI APP", BRAND.upper())
    text = text.replace("GLLYZI-", PREFIX + "-")
    text = text.replace("[gllyzi]", "[softch3at]")
    text = text.replace("gllyzi-content", "softch3at-content")
    text = text.replace("gllyzi-", "softch3at-")
    # Cross-file technical identifiers are kept unchanged if rename isn't guaranteed.
    return text


def swift_brand() -> None:
    swift_files = list(ROOT.glob("*.swift")) + list(ROOT.glob("ThreeOneOSFive/**/*.swift"))
    for path in swift_files:
        original = read(path)
        text = replace_base(original)
        # Visible standalone word/title in quoted UI strings; never rename Swift symbols.
        text = re.sub(r'(?<=")GLLYZI(?=[^"\n]*")', PREFIX, text)
        text = text.replace('"Gllyzi"', '"Software Ch3at"')
        # Separate app's device license/cache from Glizzy; avoid changing patch filesystem paths.
        text = text.replace('"gllyzi.license.', '"softch3at.license.')
        # Old bundled special key is a single constant string, not payload filename.
        text = text.replace('GLLYZI-ESPECIAL927394HD', PREFIX + '-ESPECIAL927394HD')
        # New sb_publishable keys are not JWTs; apikey header is sufficient for anonymous RPCs.
        # Passing them as Authorization: Bearer triggers Invalid JWT in current Supabase.
        text = text.replace('        request.setValue("Bearer \\(SupabaseLicenseConfig.publishableKey)", forHTTPHeaderField: "Authorization")\n', '')
        # Project-wide literal links: don't alter sync behavior.
        text = re.sub(r'https://www\.tiktok\.com/[^"\s]+', TIKTOK, text)
        text = re.sub(r'https://discord\.gg/[^"\s]+', DISCORD, text)
        text = text.replace('@glizzynetx', '@soyenyercitord')
        text = text.replace('Comunidad Glizzy', 'Comunidad Software Ch3at')
        if path.name == "DesignSystem.swift":
            text = re.sub(r'static let accent = Color\(red:[^\n]+',
                          'static let accent = Color(red: 0.64, green: 0.20, blue: 0.93)', text)
            text = re.sub(r'static let accentGlow = Color\(red:[^\n]+',
                          'static let accentGlow = Color(red: 0.83, green: 0.55, blue: 1.00)', text)
            # This asset name is still GllyziLogo for compatibility with the Xcode catalog.
        if path.name == 'ContentView.swift':
            text = re.sub(r'(?m)^\s*SocialLinkRow\(title: "(?:WhatsApp|YouTube)",[^\n]*\)\s*$', '', text)
            # Remove old company's WhatsApp and YouTube buttons (not authorised new links).
        write(path, text)



def social_brand() -> None:
    path = ROOT / 'ContentView.swift'
    content = read(path)
    marker = '                deviceSection\n\n                if appState.kernelExploitApplicable'
    if marker not in content or 'Software Ch3at - Official Social Links' in content:
        return
    section = f'''                // Software Ch3at - Official Social Links
                Section("Redes oficiales") {{
                    Link(destination: URL(string: "{TIKTOK}")!) {{
                        Label("TikTok · @soyenyercitord", systemImage: "play.rectangle.fill")
                    }}
                    Link(destination: URL(string: "{DISCORD}")!) {{
                        Label("Discord · Comunidad Software Ch3at", systemImage: "person.2.fill")
                    }}
                }}

'''
    write(path, content.replace(marker, section + marker))

def xcode_brand() -> None:
    info = ROOT / 'ThreeOneOSFive/Info.plist'
    data = read(info).replace('Glizzy Net', BRAND)
    data = data.replace('gllyzi app', BRAND)
    ET.fromstring(data)
    write(info, data)
    pbx = ROOT / 'ThreeOneOSFive.xcodeproj/project.pbxproj'
    text = read(pbx)
    text = re.sub(r'INFOPLIST_KEY_CFBundleDisplayName\s*=\s*"(?:Glizzy Net|Software Ch3at)"\s*;',
                  f'INFOPLIST_KEY_CFBundleDisplayName = "{BRAND}";', text)
    write(pbx, text)
    icon = ROOT / 'ThreeOneOSFive/Assets.xcassets/AppIcon.appiconset/AppIcon-1024.png'
    logo = ROOT / 'ThreeOneOSFive/Assets.xcassets/GllyziLogo.imageset/GllyziLogo.png'
    for src, dst in ((ROOT / 'branding/AppIcon-1024.png', icon),
                     (ROOT / 'branding/SoftCh3atLogo.png', logo),
                     (ROOT / 'branding/SoftCh3atLogo.png', ROOT / 'admin/gllyzi-logo.png')):
        dst.parent.mkdir(parents=True, exist_ok=True)
        if not dst.exists() or dst.read_bytes() != src.read_bytes():
            shutil.copy2(src, dst)
            CHANGED.append(str(dst.relative_to(ROOT)))


def admin_brand() -> None:
    html_path = ROOT / 'admin/index.html'
    html = replace_base(read(html_path))
    # Same single admin page, with two internal tabs, not a second website.
    html = html.replace('value="2008yashirchavez@gmail.com"', f'value="{ADMIN_EMAIL}"')
    html = re.sub(r'\s*<option value="(?:2008yashirchavez@gmail.com|emmajestevex@gmail.com|grego23500@gmail.com)"></option>', '', html)
    html = html.replace('Panel de archivos', 'Panel de administración')
    html = html.replace('src="./gllyzi-logo.png"', 'src="./gllyzi-logo.png"')
    write(html_path, html)
    js_path = ROOT / 'admin/app.js'
    js = replace_base(read(js_path))
    # Cross-file admin functions used only within this JS file; rename consistently.
    js = js.replace('GLLYZI', PREFIX).replace('gllyzi', 'softch3at')
    js = js.replace('Glizzy', 'Software Ch3at')
    # Preserve public URLs; no secret keys are ever embedded.
    write(js_path, js)
    css_path = ROOT / 'admin/styles.css'
    css = read(css_path)
    overrides = '''
/* --- Software Ch3at purple identity (UI-only overrides) --- */
:root {
  --bg:#06020d; --panel:#100a1c; --panel-strong:#20112f;
  --line:#36244b; --line-hot:#713cb0; --text:#fcf9ff;
  --muted:#b2a3c5; --accent:#a13ceb; --accent-strong:#ce8dff;
  --blue:#bc70ff;
}
body {
 background: radial-gradient(circle at 18% -10%, rgba(149,62,222,.23), transparent 42%),
             radial-gradient(circle at 88% 18%,rgba(100,30,159,.17),transparent 32%),
             linear-gradient(165deg,#0d0618,var(--bg));
}
.panel { border-radius:18px; background:linear-gradient(150deg,#21132f,#0f0a17); }
.tabButton.active,.primary {background:linear-gradient(135deg,#7c26cf,#b65af4);}
.topbar {border-bottom:1px solid rgba(180,122,240,.19);margin-bottom:20px;}
.brandLockup img {object-fit:contain;background:#08050d;}
button:focus-visible, input:focus-visible {outline:2px solid #ce8dff;outline-offset:3px;}
@media(max-width:700px){.topbar{flex-wrap:wrap} .shell{width:min(100% - 24px,1180px)}}
'''
    if 'Software Ch3at purple identity' not in css:
        write(css_path, css.rstrip() + '\n' + overrides)


def sql_brand() -> None:
    # Use Glizzy's exact complete production schema: its RPCs and sync remain unchanged.
    original = read(ROOT / 'supabase/setup_all.sql')
    sql = original.replace('Glizzy Net', BRAND).replace('GLLYZI', PREFIX).replace('gllyzi', 'softch3at')
    sql = sql.replace('Glizzy', BRAND)
    # No former company's admins in the new business database.
    admin_function = '''create or replace function public.is_license_admin()
returns boolean
language sql
security definer
set search_path = public
as $$
    select exists (
      select 1 from public.license_admins where user_id = (select auth.uid())
    );
$$;'''
    pat = r'create or replace function public\.is_license_admin\(\)\s*returns boolean\s*language sql\s*security definer\s*set search_path\s*=\s*public\s*as \$\$[\s\S]*?\$\$;'
    sql, n = re.subn(pat, lambda m: admin_function, sql, flags=re.I)
    if n < 1: raise RuntimeError('No se pudo neutralizar is_license_admin del original')
    # Only the new Supabase account can become admin, IF an Auth user already exists.
    pat_seed = (r'insert into public\.license_admins\s*\(user_id,\s*role\)\s*'
                r'select id,\s*\'founder\'\s*from auth\.users\s*where lower\(email\) in \([\s\S]*?\)\s*'
                r'on conflict \(user_id\) do update\s*set role = excluded\.role;')
    seed = f'''insert into public.license_admins (user_id, role)
select id, 'founder' from auth.users
where lower(email) = '{ADMIN_EMAIL}'
on conflict (user_id) do update set role = excluded.role;'''
    sql, nseed = re.subn(pat_seed, lambda m: seed, sql, flags=re.I)
    if nseed < 1: raise RuntimeError('No se pudo eliminar la lista de administradores de Glizzy')
    # Avoid seeding a shared hardcoded valid key from Glizzy (full schema otherwise preserved).
    sql = re.sub(r"insert into public\.licenses\s*\(license_key,\s*label,\s*capabilities,\s*status,\s*is_active\)\s*values\s*\([\s\S]*?\)\s*on conflict \(license_key\) do update\s*set[\s\S]*?updated_at = now\(\);", 
                 '-- Sin licencia especial prepublicada: crear keys aleatorias desde el panel admin.\n', sql, flags=re.I)
    sql = '''-- SOFTWARE CH3AT - BASE DE DATOS INDEPENDIENTE\n-- Completo y derivado de supabase/setup_all.sql de Glizzy.\n-- Ejecutar solo en el Supabase NUEVO; no ejecutar en el proyecto de Glizzy.\n-- Primero crear el usuario Auth de softwareapp98@gmail.com si no existe.\n-- Nunca agregar una secret/service_role key al codigo publico.\n\n''' + sql
    if re.search(r'2008yashirchavez|emmajestevex@gmail|grego23500|zffwtixmbuctinffojwe|gllyzi', sql, flags=re.I):
        raise RuntimeError('Se encontró una referencia privada anterior en el nuevo SQL')
    write(ROOT / 'supabase/setup_softch3at.sql', sql)


def readme() -> None:
    text = '''# Software Ch3at - implementación independiente

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
'''
    write(ROOT / 'SOFTWARE_CH3AT_INSTRUCCIONES.md', text)
    write(ROOT / 'README.md', """# Software Ch3at

App iOS y panel de administración independientes con marca morada/negra.

- Supabase propio: https://jtifsqolnkxrououonjs.supabase.co
- Keys: SOFTCH3AT-... (se crean desde el panel)
- Web única: admin/index.html (Archivos y Keys son dos pestañas)
- SQL completo: supabase/setup_softch3at.sql
- Compilación de IPA: Actions -> Software Ch3at - SQL, Panel y IPA

Consulta SOFTWARE_CH3AT_INSTRUCCIONES.md para el procedimiento y advertencias.
""")


def verify() -> None:
    must = {
       'ThreeOneOSFive/Info.plist': BRAND,
       'admin/app.js': NEW_URL,
       'supabase/setup_softch3at.sql': 'create or replace function public.activate_license',
       'admin/index.html': BRAND,
       'DesignSystem.swift': '0.64, green: 0.20, blue: 0.93',
    }
    for path, needle in must.items():
        s = read(ROOT / path)
        if needle not in s:
            raise AssertionError(f'{path} no contiene {needle!r}')
    if OLD_URL in read(ROOT / 'admin/app.js') or OLD_URL in read(ROOT / 'App.swift'):
        raise AssertionError('Un cliente sigue apuntando al Supabase de Glizzy')
    if OLD_PUBLIC_KEY in read(ROOT / 'admin/app.js') or OLD_PUBLIC_KEY in read(ROOT / 'App.swift'):
        raise AssertionError('Un cliente conserva la publishable key de Glizzy')
    if len(read(ROOT / 'supabase/setup_softch3at.sql')) < 25000:
        raise AssertionError('SQL incompleto; cancelando entrega')
    ET.fromstring(read(ROOT / 'ThreeOneOSFive/Info.plist'))
    assert (ROOT / 'ThreeOneOSFive/Assets.xcassets/AppIcon.appiconset/AppIcon-1024.png').is_file()
    assert (ROOT / 'admin/gllyzi-logo.png').is_file()
    print('Verificación estática de marca: OK (NO equivale a compilación ni ejecución SQL)')


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument('--verify', action='store_true')
    args = p.parse_args()
    if args.verify: verify(); return
    required = ['App.swift','ContentView.swift','DesignSystem.swift',
                'admin/index.html','admin/app.js','admin/styles.css',
                'supabase/setup_all.sql', 'ThreeOneOSFive.xcodeproj/project.pbxproj']
    for path in required: read(ROOT / path)
    swift_brand()
    social_brand()
    xcode_brand()
    admin_brand()
    sql_brand()
    readme()
    verify()
    print(json.dumps({'changed': CHANGED},indent=2,ensure_ascii=False))

if __name__ == '__main__':
    main()
