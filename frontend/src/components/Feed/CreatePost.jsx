import { useState } from 'react';
import { postsAPI } from '../../api/api';

export default function CreatePost({ onPostCreated }) {
    const [title, setTitle] = useState('');
    const [content, setContent] = useState('');
    const [category, setCategory] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            await postsAPI.createPost(title, content, category);
            setTitle('');
            setContent('');
            setCategory('');
            onPostCreated();
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="create-post-section">
            <h3>Создать пост</h3>
            <form onSubmit={handleSubmit}>
                <div className="form-group">
                    <label htmlFor="title">Заголовок</label>
                    <input
                        type="text"
                        id="title"
                        value={title}
                        onChange={(e) => setTitle(e.target.value)}
                        required
                        maxLength={200}
                    />
                </div>
                <div className="form-group">
                    <label htmlFor="content">Содержание</label>
                    <textarea
                        id="content"
                        value={content}
                        onChange={(e) => setContent(e.target.value)}
                        required
                        rows={4}
                    />
                </div>
                <div className="form-group">
                    <label htmlFor="category">Категория</label>
                    <select
                        id="category"
                        value={category}
                        onChange={(e) => setCategory(e.target.value)}
                        required
                    >
                        <option value="">Выберите категорию</option>
                        <option value="maintenance">обслуживание</option>
                        <option value="upgrade">апгрейд</option>
                        <option value="route">маршрут</option>
                        <option value="tricks">трюки</option>
                    </select>
                </div>
                {error && <p style={{ color: 'red' }}>{error}</p>}
                <button type="submit" className="btn btn-primary" disabled={loading}>
                    {loading ? 'Публикация...' : 'Опубликовать'}
                </button>
            </form>
        </div>
    );
}
