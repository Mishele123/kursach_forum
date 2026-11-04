import { useParams, Link } from 'react-router-dom';
import { usePost } from '../hooks/usePost';
import PostCard from '../components/posts/PostCard';
import Comments from '../components/posts/Comments';
import { Loading } from '../components/common';
export default function PostDetailPage() {
  const { id } = useParams();
  const { post, isLoading, error } = usePost(Number(id));
  return <section className="velo-page"><Link to="/feed">← Вернуться в ленту</Link>{isLoading ? <Loading /> : error || !post ? <p role="alert">Публикация не найдена или недоступна.</p> : <><PostCard post={post} /><Comments key={post.id} postId={post.id} /></>}</section>;
}
