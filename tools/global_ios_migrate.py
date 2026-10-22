#!/usr/bin/env python3
"""Copy the public Software Ch3at repository into a separate GLOBAL IOS repo.

Only run on app-global. Does NOT modify the source repo, original logic or databases.
The SQL file is generated from the COMPLETE original setup_all.sql (not a summary).
"""
from __future__ import annotations
import argparse
import re
import shutil
import sys
import json
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BRAND = "GLOBAL IOS"
REF = "tqdbvswgpmtbfezwucli"
URL = f"https://{REF}.supabase.co"
KEY = "sb_publishable_dR7EYTs81scCKwgWNkwFug_2Y4scFhh"
PREFIX = "GLOBALIOS"
BUCKET = "globalios-content"
BUNDLE_ID = "com.globalios.client"
OLD_REFS = ("zffwtixmbuctinffojwe", "jtifsqolnkxrououonjs")
OLD_KEYS = (
    "sb_publishable_6xRmOLD0Cw4Dtwn460l_Zw_Y7khT6wA",
    "sb_publishable_vVlLdGyUErtzRfSyPU426g_WqVACybG",
)
CHANGES: list[str] = []


def read(relative: str) -> str:
    p = ROOT / relative
    if not p.is_file():
        raise FileNotFoundError(f"Falta {relative}; no se puede continuar.")
    return p.read_text(encoding='utf-8-sig')


def put(relative: str, content: str) -> None:
    p = ROOT / relative
    p.parent.mkdir(parents=True, exist_ok=True)
    if not p.exists() or p.read_text(encoding='utf-8-sig') != content:
        p.write_text(content, encoding='utf-8')
        CHANGES.append(relative)


def clone_files(base: Path) -> None:
    base = base.resolve()
    if base == ROOT.resolve() or not (base / 'admin/app.js').is_file() or not (base / 'supabase/setup_all.sql').is_file():
        raise ValueError('La base debe ser el checkout publico completo de app-software')
    # Do not copy Software Ch3at workflows, tools, original repository metadata or brand assets.
    skip = {'.git', '.github', 'branding', 'tools', '.build', 'README.md',
            'LEEME_SUBIR_A_GITHUB.txt', 'SOFTWARE_CH3AT_INSTRUCCIONES.md',
            'Software_Ch3at_Instalador', '.globalios-base'}
    for obj in base.iterdir():
        if obj.name in skip or obj.name.startswith('SOFTWARE_CH3AT'):
            continue
        dst = ROOT / obj.name
        if obj.is_symlink():
            continue
        if obj.is_dir():
            shutil.copytree(obj, dst, dirs_exist_ok=True, symlinks=False)
        elif obj.is_file():
            shutil.copy2(obj, dst)
    CHANGES.append('codigo de app-software copiado a app-global')


def rebrand(t: str) -> str:
    for ref in OLD_REFS:
        t = t.replace(f'https://{ref}.supabase.co', URL)
        t = t.replace(ref, REF)
    for old in OLD_KEYS:
        t = t.replace(old, KEY)
    for old in ('Software Ch3at', 'SOFTWARE CH3AT', 'Glizzy Net', 'GLIZZY NET',
                'gllyzi app', 'GLLYZI APP', 'GLIZZY APP'):
        t = t.replace(old, BRAND)
    t = t.replace('SOFTCH3AT-', PREFIX + '-').replace('GLLYZI-', PREFIX + '-')
    t = t.replace('SOFTCH3AT', PREFIX).replace('GLLYZI', PREFIX)
    t = t.replace('softch3at-', 'globalios-').replace('gllyzi-', 'globalios-')
    t = t.replace('[softch3at]', '[globalios]').replace('[gllyzi]', '[globalios]')
    t = t.replace('softch3at-content', BUCKET).replace('gllyzi-content', BUCKET)
    t = t.replace('Glizzy', BRAND).replace('gllyzi', 'globalios')
    t = t.replace('SoftCh3at', 'GlobalIOS')
    return t


def strip_social_sections(text: str) -> str:
    """Remove entire nested SwiftUI social Section blocks safely."""
    for prefix in ('Section("Redes oficiales")', 'Section("Redes sociales")'):
        while prefix in text:
            at = text.find(prefix)
            line_start = text.rfind('\n', 0, at) + 1
            b = text.find('{', at + len(prefix))
            if b < 0: raise ValueError('Sección social mal formada')
            depth = 0
            end = None
            for i in range(b, len(text)):
                if text[i] == '{': depth += 1
                if text[i] == '}':
                    depth -= 1
                    if depth == 0:
                        end = i + 1
                        break
            if end is None: raise ValueError('Sección social sin llave final')
            text = text[:line_start] + text[end:].lstrip('\r\n')
    return text


def remove_social_link_cards(text: str) -> str:
    """Remove a complete nested SwiftUI Link card, never only its opening line.

    The prior migration removed just the URL-bearing Link opening, leaving its
    HStack and closing brace behind and breaking PatchProjectsView.swift.
    Do not touch Apply / Restore buttons or content synchronization.
    """
    social_hosts = (
        'tiktok.com/', 'discord.gg/', 'chat.whatsapp.com/',
        'youtube.com/', 'youtu.be/',
    )
    while True:
        match = re.search(r'(?m)^[ \t]*Link\s*\(destination:\s*URL\(string:\s*"https?://[^"\n]+"\)!\)\s*\{', text)
        if match is None:
            return text
        snippet = match.group(0).lower()
        if not any(host in snippet for host in social_hosts):
            # Leave unrelated functional links untouched; scan further.
            rest_start = match.end()
            later = remove_social_link_cards(text[rest_start:])
            return text[:rest_start] + later
        start = match.start()
        brace = text.rfind('{', match.start(), match.end())
        depth = 0
        end = None
        for i in range(brace, len(text)):
            if text[i] == '{':
                depth += 1
            elif text[i] == '}':
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
        if end is None:
            raise ValueError('Link social sin llave final')
        text = text[:start] + text[end:].lstrip('\r\n')


def ios() -> None:
    for p in list(ROOT.glob('*.swift')) + list(ROOT.glob('ThreeOneOSFive/**/*.swift')):
        original = p.read_text(encoding='utf-8-sig')
        # Remove a whole social card BEFORE replacing its URL. A line-only
        # removal leaves an unmatched closing brace and breaks Xcode builds.
        s = rebrand(remove_social_link_cards(original))
        # Physical paths/payload names in the patch engine must stay valid.
        # An old payload filename is a technical part of the source and not brand UI.
        s = s.replace('assetindexer.globalios-especial927394hd', 'assetindexer.gllyzi-especial927394hd')
        # Reset licence/cache keys so this installation cannot reuse other companies' licences.
        s = s.replace('"softch3at.license.', '"globalios.license.')
        s = s.replace('"gllyzi.license.', '"globalios.license.')
        s = s.replace('MobileHouseArrest.globalios-license', 'globalios.client-license')
        # Publishable keys are not JWTs; the API key header is sufficient for anonymous RPCs.
        s = "".join(line for line in s.splitlines(keepends=True) if not ('request.setValue("Bearer ' in line and 'SupabaseLicenseConfig.publishableKey' in line and 'forHTTPHeaderField: "Authorization"' in line))
        # Remove Ch3at social menu (if installed) without affecting device/patch sections.
        if p.name == 'ContentView.swift':
            s = strip_social_sections(s)
            # Alternative legacy SocialLinkRow lines, if present in source.
            s = re.sub(r'(?m)^\s*SocialLinkRow\(title: "(?:TikTok|Discord|WhatsApp|YouTube)"[^\n]*\n', '', s)
            s = re.sub(r'(?m)^\s*Text\("Canales de soporte, comunidad y actualizaciones[^\n]*\n', '', s)
            # Prevent showing a social tab if the variant has one: keep feature logic and enum intact.
            s = s.replace('case .social: return "Redes"', 'case .social: return "Servicios"')
        # Avoid calls to previous companies' communities anywhere in Swift UI.
        s = re.sub(r'https://(?:www\.)?tiktok\.com/[^"\s]+', 'https://example.invalid', s)
        s = re.sub(r'https://discord\.gg/[^"\s]+', 'https://example.invalid', s)
        s = re.sub(r'https://chat\.whatsapp\.com/[^"\s]+', 'https://example.invalid', s)
        s = re.sub(r'https://youtube\.com/[^"\s]+', 'https://example.invalid', s)
        # Never leave dead social buttons in GLOBAL IOS (avoid dangling dummy URLs)
        if 'example.invalid' in s:
            s = re.sub(r'(?m)^.*(?:SocialLinkRow|Link\(destination:).*(?:example\.invalid).*\n', '', s)
        if p.name == 'DesignSystem.swift':
            s = re.sub(r'static let accent = Color\(red:[^\n]+', 'static let accent = Color(red: 0.72, green: 0.72, blue: 0.75)', s)
            s = re.sub(r'static let accentGlow = Color\(red:[^\n]+', 'static let accentGlow = Color(red: 0.90, green: 0.90, blue: 0.93)', s)
            s = s.replace('UIImage(named: "GllyziLogo")', 'UIImage(named: "GlobalIOSLogo")')
        if original != s:
            put(str(p.relative_to(ROOT)), s)

    info = 'ThreeOneOSFive/Info.plist'
    xml = rebrand(read(info))
    xml = re.sub(r'(<key>CFBundleDisplayName</key>\s*<string>).*?(</string>)', r'\g<1>GLOBAL IOS\2', xml)
    xml = re.sub(r'(<key>CFBundleName</key>\s*<string>).*?(</string>)', r'\g<1>GLOBAL IOS\2', xml)
    # Unique bundle identity so it cannot replace Ch3at/Glizzy on the iPhone.
    xml = re.sub(r'(<key>CFBundleIdentifier</key>\s*<string>).*?(</string>)', lambda m:m.group(1)+BUNDLE_ID+m.group(2),xml)
    ET.fromstring(xml)
    put(info,xml)
    pbx = 'ThreeOneOSFive.xcodeproj/project.pbxproj'
    v = read(pbx)
    v = re.sub(r'INFOPLIST_KEY_CFBundleDisplayName\s*=\s*"[^"]*";', 'INFOPLIST_KEY_CFBundleDisplayName = "GLOBAL IOS";', v)
    v = re.sub(r'PRODUCT_BUNDLE_IDENTIFIER\s*=\s*"[^"]*";', f'PRODUCT_BUNDLE_IDENTIFIER = "{BUNDLE_ID}";', v)
    put(pbx,v)
    ac = ROOT / 'ThreeOneOSFive/Assets.xcassets'
    icon = ac / 'AppIcon.appiconset/AppIcon-1024.png'
    icon.parent.mkdir(parents=True,exist_ok=True)
    src_icon = ROOT/'branding/AppIcon-1024.png'
    if not icon.exists() or icon.read_bytes() != src_icon.read_bytes():
        shutil.copy2(src_icon,icon)
        CHANGES.append(str(icon.relative_to(ROOT)))
    glogo = ac / 'GlobalIOSLogo.imageset'
    glogo.mkdir(parents=True,exist_ok=True)
    shutil.copy2(ROOT/'branding/GlobalIOSLogo.png', glogo/'GlobalIOSLogo.png')
    put(str((glogo/'Contents.json').relative_to(ROOT)), json.dumps({'images':[{'filename':'GlobalIOSLogo.png','idiom':'universal','scale':'1x'},{'idiom':'universal','scale':'2x'},{'idiom':'universal','scale':'3x'}],'info':{'author':'xcode','version':1}},indent=2)+'\n')
    # Remove obsolete resource to avoid mixing brand assets, not code or patches.
    legacy = ac / 'GllyziLogo.imageset'
    if legacy.is_dir():shutil.rmtree(legacy)


def admin() -> None:
    html='admin/index.html'
    h=rebrand(read(html))
    h=re.sub(r'(?i)<title>.*?</title>','<title>GLOBAL IOS · Administración</title>',h,count=1)
    h=h.replace('Panel de archivos', 'Panel de administración')
    h=h.replace('src="./gllyzi-logo.png"','src="./global-ios-logo.png"').replace('src="./globalios-logo.png"','src="./global-ios-logo.png"')
    h=re.sub(r'(<input[^>]*id="emailInput"[^>]*?)\s+value="[^"]*"',r'\1',h)
    h=re.sub(r'(?m)^\s*<option value="[^"]+@[^\"]+"></option>\s*$', '', h)
    h=rebrand(h)
    put(html,h)
    js='admin/app.js'
    s=rebrand(read(js))
    s=s.replace('gllyzi-logo.png','global-ios-logo.png').replace('globalios-logo.png','global-ios-logo.png')
    s=s.replace('"gllyzi-content"', '"globalios-content"').replace('"softch3at-content"','"globalios-content"')
    # Old business emails were prefills only; never authorize by string in client.
    s=re.sub(r'2008yashirchavez@gmail\.com|emmajestevex@gmail\.com|grego23500@gmail\.com|softwareapp98@gmail\.com','',s)
    put(js,s)
    css='admin/styles.css'
    s=read(css)
    if '/* GLOBAL IOS PALETTE */' not in s:
        s+='''\n/* GLOBAL IOS PALETTE */\n:root{--bg:#070707;--panel:#131313;--panel-strong:#202022;--line:#353537;--line-hot:#6c6c72;--text:#f7f7f8;--muted:#b0b0b9;--accent:#dedee2;--accent-strong:#fff;--blue:#bfc2c9;}\nbody{background:radial-gradient(circle at 50% -30%,#313137 0%,#0b0b0e 54%,#060607 100%);color:#f8f8fa;}\n.panel{border-radius:18px;background:linear-gradient(148deg,#1d1d20,#111113);border-color:#38383d;}\n.tabButton.active,.primary{background:linear-gradient(135deg,#f4f4f6,#b5b5bb);color:#0b0b0e;box-shadow:0 6px 26px rgba(255,255,255,.12);}\n.topbar{border-bottom:1px solid #333338;padding-bottom:14px;}\n.brandLockup img{object-fit:contain;background:white;border-radius:14px;}\na,button:focus-visible,input:focus-visible{outline-color:#d4d4da;}\n@media(max-width:700px){.topbar{flex-wrap:wrap}.shell{width:min(100% - 22px,1180px)}.gridInner,.keysGrid{grid-template-columns:1fr;}}\n'''
    put(css,s)
    img=ROOT/'admin/global-ios-logo.png'
    shutil.copy2(ROOT/'branding/GlobalIOSLogo.png',img)
    legacy=ROOT/'admin/gllyzi-logo.png'
    if legacy.exists(): legacy.unlink()
    # One web panel with two tabs is retained. No separate user-facing second site.


def sql() -> None:
    source=read('supabase/setup_all.sql')
    text=rebrand(source)
    # Replace all inherited role checks, several copies can appear in the source.
    pat=r'create or replace function public\.is_license_admin\(\)\s*returns boolean\s*language sql\s*security definer\s*set search_path\s*=\s*public\s*as \$\$[\s\S]*?\$\$;'
    new='''create or replace function public.is_license_admin()\nreturns boolean\nlanguage sql\nsecurity definer\nset search_path = public\nas $$\n  select exists (select 1 from public.license_admins where user_id = (select auth.uid()));\n$$;'''
    text,n=re.subn(pat,lambda _:new,text,flags=re.I)
    if n<1: raise ValueError('SQL original sin función is_license_admin. No se puede asegurar aislamiento.')
    pat_seed=(r'insert into public\.license_admins\s*\(user_id,\s*role\)\s*'
              r'select id,\s*\'founder\'\s*from auth\.users\s*where lower\(email\) in \([\s\S]*?\)\s*'
              r'on conflict \(user_id\) do update\s*set role = excluded\.role;')
    text,nseed=re.subn(pat_seed,'-- No se copian administradores de otras empresas. Ver ASIGNAR_ADMIN_GLOBAL_IOS.sql.',text,flags=re.I)
    if nseed<1: raise ValueError('No se pudieron retirar todos los administradores originales')
    # No ship a usable hard-coded key copied from either company.
    pat_key=(r'insert into public\.licenses\s*\(license_key,\s*label,\s*capabilities,\s*status,\s*is_active\)\s*'
             r'values\s*\([\s\S]*?\)\s*on conflict \(license_key\) do update\s*set[\s\S]*?updated_at = now\(\);')
    text,nkeys=re.subn(pat_key,'-- No se importa licencia especial; generar keys desde GLOBAL IOS Admin.',text,flags=re.I)
    if nkeys<1: raise ValueError('No se pudo retirar la licencia especial de la marca anterior')
    if re.search('(?:2008yashirchavez|emmajestevex@gmail|grego23500|softwareapp98@gmail|softch3at|gllyzi|zffwtixmbuctinffojwe|jtifsqolnkxrououonjs)',text,re.I):
        raise ValueError('El SQL contiene una referencia a otra empresa')
    header='''-- GLOBAL IOS - ESQUEMA COMPLETO INDEPENDIENTE\n-- Generado del SQL COMPLETO de app-software (Glizzy/Software Ch3at).\n-- Ejecutar SOLO en el proyecto Supabase app global, ref tqdbvswgpmtbfezwucli.\n-- No crea administradores ni licencias de otra empresa.\n-- Separa las claves GLOBALIOS-, sus categorías y el bucket globalios-content.\n-- Ejecútalo como dueño de la BD, luego asigna TU usuario Auth como administrador.\n\n'''
    put('supabase/SETUP_GLOBAL_IOS_COMPLETO.sql',header+text)
    put('supabase/ASIGNAR_ADMIN_GLOBAL_IOS.sql','''-- Ejecútalo SOLO después de SETUP_GLOBAL_IOS_COMPLETO.sql.\n-- Crea primero tu cuenta en Authentication > Users del proyecto GLOBAL IOS.\n-- SUSTITUYE CAMBIA_AQUI_TU_EMAIL por el correo real de esa cuenta.\nDO $$\nDECLARE v_email text := 'CAMBIA_AQUI_TU_EMAIL';\nDECLARE v_user_id uuid;\nBEGIN\n  IF v_email = 'CAMBIA_AQUI_TU_EMAIL' THEN\n    RAISE EXCEPTION 'Debes escribir tu propio correo del usuario Auth de GLOBAL IOS';\n  END IF;\n  SELECT id INTO v_user_id FROM auth.users WHERE lower(email)=lower(trim(v_email));\n  IF v_user_id IS NULL THEN\n    RAISE EXCEPTION 'El usuario no existe en Authentication > Users de GLOBAL IOS';\n  END IF;\n  INSERT INTO public.license_admins (user_id,role) VALUES(v_user_id,'founder')\n  ON CONFLICT (user_id) DO UPDATE SET role=EXCLUDED.role;\nEND $$;\n''')


def docs() -> None:
    put('README.md', '''# GLOBAL IOS\n\nProyecto iOS y panel de administración NUEVOS, basados en el código de `app-software`, con backend independiente.\n\n- Repo destino: **emmajestevex-ui/app-global**. Repo origen solo lectura: **emmajestevex-ui/app-software**.\n- Nombre: **GLOBAL IOS**. Tema blanco/negro/gris. Sin redes sociales.\n- Supabase destino: https://tqdbvswgpmtbfezwucli.supabase.co\n- Key pública: `sb_publishable_dR7EYTs81scCKwgWNkwFug_2Y4scFhh` (NO es una clave de administrador).\n- Prefijo licencias `GLOBALIOS-`. Bucket `globalios-content`.\n- Una sola web admin/index.html, con pestañas de Archivos y Keys.\n- SQL de instalación: `supabase/SETUP_GLOBAL_IOS_COMPLETO.sql`.\n- SQL para asignar ADMIN: `supabase/ASIGNAR_ADMIN_GLOBAL_IOS.sql` (personalizar correo).\n- Workflow: Actions > GLOBAL IOS - Migrar, SQL, Panel e IPA.\n\n**Importante:** Clave, usuarios Auth, tablas, datos, Storage y panel deben pertenecer al **nuevo proyecto**. No copiamos datos de otras empresas. El SQL y la IPA aún necesitan pruebas reales.\n\nEl CFBundleIdentifier ahora es `com.globalios.client` para evitar colisiones de instalación con otras apps; verificar que las funciones del app base sigan funcionando en el dispositivo.\n\nEl logo proporcionado se parece al de Apple: para distribución comercial verifica tus derechos de uso de esa marca. Este proyecto NO es una aplicación oficial de Apple.\n''')


def verify() -> None:
    required={'admin/index.html':BRAND,'admin/app.js':URL,'App.swift':URL,'ThreeOneOSFive/Info.plist':BRAND,'supabase/SETUP_GLOBAL_IOS_COMPLETO.sql':'create or replace function public.activate_license','supabase/ASIGNAR_ADMIN_GLOBAL_IOS.sql':'CAMBIA_AQUI_TU_EMAIL'}
    for f,t in required.items():
        if t not in read(f):raise AssertionError(f'Falta {t} en {f}')
    if PREFIX+'-' not in read('admin/app.js'):raise AssertionError('Prefijo de keys incorrecto')
    if BUCKET not in read('admin/app.js') or BUCKET not in read('supabase/SETUP_GLOBAL_IOS_COMPLETO.sql'):raise AssertionError('Bucket incorrecto')
    if KEY not in read('App.swift') or KEY not in read('admin/app.js'):raise AssertionError('Publishable key incorrecta')
    if 'tiktok.com' in read('ContentView.swift') or 'discord.gg' in read('ContentView.swift'):
        raise AssertionError('Se encontraron links sociales')
    if 'Redes oficiales' in read('ContentView.swift'):raise AssertionError('Se encontró menú de redes')
    detail=read('ThreeOneOSFive/views/PatchProjectsView.swift')
    if 'TikTok oficial' in detail or '@soyenyercitord' in detail:
        raise AssertionError('Quedó una tarjeta social que rompería la compilación')
    for p in ['App.swift','admin/app.js','supabase/SETUP_GLOBAL_IOS_COMPLETO.sql']:
        s=read(p)
        if any(old in s for old in OLD_REFS+OLD_KEYS):raise AssertionError('Conexión vieja en '+p)
    if len(read('supabase/SETUP_GLOBAL_IOS_COMPLETO.sql'))<25000:raise AssertionError('SQL incompleto')
    ET.fromstring(read('ThreeOneOSFive/Info.plist'))
    if not (ROOT/'admin/global-ios-logo.png').exists():raise AssertionError('Logo web perdido')
    if 'src="./global-ios-logo.png"' not in read('admin/index.html'):raise AssertionError('El logo del panel no coincide con su archivo')
    print('Validación estática: OK. No equivale a compilación real ni ejecución SQL.')


def main()->None:
    parser=argparse.ArgumentParser()
    parser.add_argument('--base',help='Carpeta local con checkout de emmajestevex-ui/app-software')
    parser.add_argument('--verify',action='store_true')
    a=parser.parse_args()
    if a.verify:verify();return
    if a.base:clone_files(Path(a.base))
    for name in ['App.swift','ContentView.swift','DesignSystem.swift','admin/index.html','admin/app.js','admin/styles.css','supabase/setup_all.sql','ThreeOneOSFive.xcodeproj/project.pbxproj']:
        read(name)
    ios();admin();sql();docs();verify()
    print(json.dumps({'changed':CHANGES},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
