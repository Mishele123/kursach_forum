export default function PostCard({ post }) {
    const formatDate = (dateString) => {
        const date = new Date(dateString);
        return date.toLocaleDateString('ru-RU', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    const getCategoryName = (category) => {
        const categories = {
            'maintenance': 'обслуживание',
            'upgrade': 'апгрейд',
            'route': 'маршрут',
            'tricks': 'трюки'
        };
        return categories[category] || category;
    };

    return (
        <article className="post-card">
            <div className="post-header">
                <div className="post-author">
                    <div className="author-avatar">
                        {post.author?.username?.charAt(0).toUpperCase() || '?'}
                    </div>
                    <div>
                        <div className="author-name">{post.author?.username || 'Аноним'}</div>
                        <div className="post-date">{formatDate(post.created_at)}</div>
                    </div>
                </div>
                <span className={`category-tag category-${post.category}`}>
                    {getCategoryName(post.category)}
                </span>
            </div>
            {post.photo_url && (
                <img src={post.photo_url} alt="Post" style={{ width: '100%', borderRadius: '8px', margin: '1rem 0' }} />
            )}
            <div className="post-content">
                <h3>{post.title}</h3>
                <p>{post.content}</p>
            </div>
        </article>
    );
}
