import {useState,useEffect} from 'react';
import {postsApi,errorMessage} from '../services/api';
import {useAuth} from '../context/AuthContext';
import type {Post} from '../types';
export const usePost=(postId:number)=>{
 const {user}=useAuth();const [post,setPost]=useState<Post|null>(null);const [isLoading,setLoading]=useState(true);const [error,setError]=useState<string|null>(null);
 useEffect(()=>{let active=true;setPost(null);setLoading(true);setError(null);if(!Number.isInteger(postId)||postId<1){setError('Публикация не найдена');setLoading(false);return;}
 void postsApi.getPost(postId).then(data=>{if(active)setPost(data);}).catch(err=>{if(active)setError(errorMessage(err));}).finally(()=>{if(active)setLoading(false);});return ()=>{active=false;};},[postId,user?.id]);
 return {post,isLoading,error};
};
