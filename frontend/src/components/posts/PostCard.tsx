import {useEffect,useRef,useState} from 'react';
import {Link} from 'react-router-dom';
import {postsApi,errorMessage} from '../../services/api';
import {useAuth} from '../../context/AuthContext';
import {formatRelativeTime} from '../../utils/helpers';
import AvatarImage from '../common/AvatarImage';
import Gallery from './Gallery';
import {PostLocationPreview} from './PostLocation';
import PostOwnerActions, { type PostMutationProps } from './PostOwnerActions';
import './PostCard.css';
import {CATEGORY_LABELS} from '../../utils/constants';
import type {Post} from '../../types';
export default function PostCard({post,compact=false,onUpdate,onDelete}:PostMutationProps & {post:Post;compact?:boolean}){
 const {user,isLoading}=useAuth();const [liked,setLiked]=useState(post.liked_by_me);const [count,setCount]=useState(post.like_count||0);const [busy,setBusy]=useState(false);const [error,setError]=useState('');const pending=useRef(false);
 useEffect(()=>{setLiked(post.liked_by_me);setCount(post.like_count||0);},[post.id,post.liked_by_me,post.like_count]);
 async function toggleLike(){if(pending.current)return;pending.current=true;setBusy(true);setError('');try{const result=await postsApi.setLike(post.id,!liked);setLiked(result.liked_by_me);setCount(result.like_count);}catch(err){setError(errorMessage(err));}finally{pending.current=false;setBusy(false);}}
 const isOwner = user?.id === post.author.id;
 const showActions = !isLoading && (isOwner || user?.role === 'moderator' || user?.role === 'admin');
 return <article className={`velo-card post-card${showActions ? " post-card-owner" : ""}`}><header className="post-author"><Link className="avatar" to={`/users/${post.author.id}`}><AvatarImage username={post.author.username} url={post.author.avatar_url}/></Link><div><Link to={`/users/${post.author.id}`}><strong>{post.author.username}</strong></Link><p>{formatRelativeTime(post.created_at)}</p></div></header><span className="category-badge">{CATEGORY_LABELS[post.category]}</span>{showActions && <PostOwnerActions post={post} isOwner={isOwner} onUpdate={onUpdate} onDelete={onDelete} />}<Link to={`/post/${post.id}`}><h2>{post.title}</h2></Link><p className="post-text">{post.text}</p>{post.place && <PostLocationPreview place={post.place} />}<Gallery post={post} compact={compact}/><footer><div className="post-actions">{user ? <button className="velo-button secondary" aria-pressed={!!liked} disabled={busy||isLoading} onClick={toggleLike}>{busy?'Сохраняем…':liked?'♥ Нравится':'♡ Нравится'} · {count}</button> : <Link to="/login">♡ {count} · Войти, чтобы поставить лайк</Link>}<Link to={`/post/${post.id}`}>Обсудить →</Link></div>{error&&<p role="alert" className="error">{error}</p>}</footer></article>;
}
