import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { postsApi } from '../services/api';
import PhotoUpload from '../components/common/PhotoUpload';
import type { Post } from '../types';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { usePost } from '../hooks/usePost';
import PostCard from '../components/posts/PostCard';
import Comments from '../components/posts/Comments';
import { Loading } from '../components/common';

type PostChanges = Partial<Pick<Post, 'title' | 'text' | 'category' | 'place' | 'photo_url' | 'photos'>>;

export default function PostDetailPage() {
  const { id } = useParams();
  const { user } = useAuth();
  return <PostDetail key={`${id}:${user?.id ?? 'guest'}`} postId={Number(id)} viewerId={user?.id} />;
}

function PostDetail({ postId, viewerId }: { postId: number; viewerId?: number }) {
  const navigate = useNavigate();
  const { post, isLoading, error } = usePost(postId);
  const [changes, setChanges] = useState<PostChanges>({});
  const shown = post ? { ...post, ...changes } : null;
  const remainingPhotos = 10 - (shown?.photos?.length ?? 0);

  function updatePost({ title, text, category, place }: Post) {
    setChanges(current => ({ ...current, title, text, category, place }));
  }

  async function uploadPhotos(files: File[]) {
    const { photo_url, photos } = await postsApi.addPhotos(postId, files);
    setChanges(current => ({ ...current, photo_url, photos }));
  }

  return <section className="velo-page">
    <Link to="/feed">← Вернуться в ленту</Link>
    {isLoading ? <Loading /> : error || !shown ? <p role="alert">Публикация не найдена или недоступна.</p> : <>
      <PostCard post={shown} onUpdate={updatePost} onDelete={() => navigate('/feed', { replace: true })} />
      {viewerId === shown.author.id && remainingPhotos > 0 && <div className="velo-card">
        <h2>Добавить фотографии</h2>
        <PhotoUpload maximum={remainingPhotos} upload={uploadPhotos} />
      </div>}
      <Comments postId={shown.id} />
    </>}
  </section>;
}
