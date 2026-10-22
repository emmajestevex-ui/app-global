-- Ejecútalo SOLO después de SETUP_GLOBAL_IOS_COMPLETO.sql.
-- Crea primero tu cuenta en Authentication > Users del proyecto GLOBAL IOS.
-- SUSTITUYE CAMBIA_AQUI_TU_EMAIL por el correo real de esa cuenta.
DO $$
DECLARE v_email text := 'CAMBIA_AQUI_TU_EMAIL';
DECLARE v_user_id uuid;
BEGIN
  IF v_email = 'CAMBIA_AQUI_TU_EMAIL' THEN
    RAISE EXCEPTION 'Debes escribir tu propio correo del usuario Auth de GLOBAL IOS';
  END IF;
  SELECT id INTO v_user_id FROM auth.users WHERE lower(email)=lower(trim(v_email));
  IF v_user_id IS NULL THEN
    RAISE EXCEPTION 'El usuario no existe en Authentication > Users de GLOBAL IOS';
  END IF;
  INSERT INTO public.license_admins (user_id,role) VALUES(v_user_id,'founder')
  ON CONFLICT (user_id) DO UPDATE SET role=EXCLUDED.role;
END $$;
