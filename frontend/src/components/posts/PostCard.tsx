import { mediaUrl } from '../../services/api';
import { Link } from 'react-router-dom';
import { formatRelativeTime } from '../../utils/helpers';
import AvatarImage from '../common/AvatarImage';
import { CATEGORY_LABELS } from '../../utils/constants';
import type { Post } from '../../types';
export default function PostCard({ post }: { post: Post }) {
  return <article className="velo-card post-card">
    <header className="post-author"><div className="avatar"><AvatarImage username={post.author.username}  /></div><div><strong>{post.author.username}</strong><p>{formatRelativeTime(post.created_at)}</p></div></header>
    <span className="category-badge">{CATEGORY_LABELS[post.category]}</span>
    <Link to={`/post/${post.id}`}><h2>{post.title}</h2></Link>
    <p className="post-text">{post.text}</p>
    {post.photo_url && <img src={mediaUrl(post.photo_url)} alt={post.title} loading="lazy" />}
    <footer><Link to={`/post/${post.id}`}>Читать публикацию →</Link></footer>
  </article>;
}
