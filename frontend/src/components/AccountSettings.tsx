import {useState} from 'react';
import type {FormEvent} from 'react';
import {authApi,errorMessage} from '../services/api';
import {Input,Button} from './common';
export default function AccountSettings(){
 const [passwordBusy,setPasswordBusy]=useState(false);const [passwordError,setPasswordError]=useState('');const [passwordNotice,setPasswordNotice]=useState('');
 async function password(e:FormEvent<HTMLFormElement>){e.preventDefault();const form=e.currentTarget;const data=new FormData(form);const next=String(data.get('new_password'));setPasswordError('');setPasswordNotice('');if(next!==data.get('confirm_password')){setPasswordError('Новые пароли не совпадают');return;}setPasswordBusy(true);try{await authApi.changePassword(String(data.get('current_password')),next);form.reset();setPasswordNotice('Пароль изменён');}catch(err){setPasswordError(errorMessage(err));}finally{setPasswordBusy(false);}}
 return <>
 <form id="account-security" className="velo-card velo-form settings-section" onSubmit={password}><h2>Сменить пароль</h2><fieldset className="profile-fields" disabled={passwordBusy}><Input label="Текущий пароль" name="current_password" type="password" required minLength={8} maxLength={128} autoComplete="current-password"/><Input label="Новый пароль" name="new_password" type="password" required minLength={8} maxLength={128} autoComplete="new-password"/><Input label="Повторите новый пароль" name="confirm_password" type="password" required minLength={8} maxLength={128} autoComplete="new-password"/></fieldset>{passwordError&&<p className="error" role="alert">{passwordError}</p>}{passwordNotice&&<p role="status">{passwordNotice}</p>}<Button type="submit" isLoading={passwordBusy}>Изменить пароль</Button></form></>;
}
