import {useEffect,useState} from 'react';
import {useAuth} from '../context/AuthContext';
import {postsApi} from '../services/api';
import PhotoUpload from '../components/common/PhotoUpload';
import type {Post} from '../types';
import { useParams, Link } from 'react-router-dom';
import { usePost } from '../hooks/usePost';
import PostCard from '../components/posts/PostCard';
import Comments from '../components/posts/Comments';
import { Loading } from '../components/common';
export default function PostDetailPage() {
  const { id } = useParams();
  const { post, isLoading, error } = usePost(Number(id));
  const {user}=useAuth();const [updated,setUpdated]=useState<Post|null>(null);
  useEffect(()=>setUpdated(null),[post]);const shown=updated||post;
  return <section className="velo-page"><Link to="/feed">← Вернуться в ленту</Link>{isLoading ? <Loading /> : error || !post ? <p role="alert">Публикация не найдена или недоступна.</p> : <><PostCard key={user?.id||"guest"} post={shown!} />{user?.id===post.author.id && (shown?.photos?.length||0)<10 && <div className="velo-card"><h2>Добавить фотографии</h2><PhotoUpload maximum={10-(shown?.photos?.length||0)} upload={async files=>setUpdated(await postsApi.addPhotos(post.id,files))}/></div>}<Comments key={post.id} postId={post.id} /></>}</section>;
}
