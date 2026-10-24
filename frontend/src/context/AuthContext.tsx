import { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import api, { authApi } from '../services/api';
import type { User, LoginDto, CreateUserDto } from '../types';
interface AuthContextType {
 user: User | null;
 isAuthenticated: boolean;
 isLoading: boolean;
 login: (credentials: LoginDto) => Promise<void>;
 register: (data: CreateUserDto) => Promise<void>;
 logout: () => void;
 refreshUser: () => Promise<void>;
}
const AuthContext = createContext<AuthContextType | undefined>(undefined);
export function useAuth() {
 const context=useContext(AuthContext);
 if(!context) throw new Error('useAuth must be used within AuthProvider');
 return context;
}
export function AuthProvider({ children }: { children: ReactNode }) {
 const [user,setUser]=useState<User | null>(null);
 const [isLoading,setIsLoading]=useState(true);
 useEffect(() => {
  let active=true;
  void authApi.getCurrentUser().then(current => {if(active) setUser(current);}).catch(() => {if(active) setUser(null);}).finally(() => {if(active) setIsLoading(false);});
  return () => {active=false;};
 },[]);
 async function login(credentials: LoginDto) {
  await authApi.login(credentials);
  setUser(await authApi.getCurrentUser());
 }
 async function register(data: CreateUserDto) {
  await authApi.register(data);
  await login({email:data.email,password:data.password});
 }
 function logout() {
  void api.post('/auth/logout').then(() => setUser(null)).catch(() => alert('Не удалось выйти. Попробуйте снова.'));
 }
 async function refreshUser() {setUser(await authApi.getCurrentUser());}
 return <AuthContext.Provider value={{user,isAuthenticated:!!user,isLoading,login,register,logout,refreshUser}}>{children}</AuthContext.Provider>;
}
