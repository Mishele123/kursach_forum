import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { usePosts } from '../hooks';
import { Button, Input, Textarea } from '../components/common';
import { POST_CATEGORIES, CATEGORY_LABELS, ROUTES, MAX_POST_TITLE_LENGTH, MAX_POST_TEXT_LENGTH } from '../utils/constants';
import type { PostCategory } from '../types';

const CreatePostPage: React.FC = () => {
  const [title, setTitle] = useState('');
  const [text, setText] = useState('');
  const [category, setCategory] = useState<PostCategory>('маршрут');
  const [photoUrl, setPhotoUrl] = useState('');
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { createPost } = usePosts();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Validation
    if (!title.trim()) {
      setError('Пожалуйста, введите заголовок');
      return;
    }

    if (!text.trim()) {
      setError('Пожалуйста, введите текст публикации');
      return;
    }

    if (title.length > MAX_POST_TITLE_LENGTH) {
      setError(`Заголовок не должен превышать ${MAX_POST_TITLE_LENGTH} символов`);
      return;
    }

    if (text.length > MAX_POST_TEXT_LENGTH) {
      setError(`Текст не должен превышать ${MAX_POST_TEXT_LENGTH} символов`);
      return;
    }

    setIsSubmitting(true);

    try {
      await createPost({
        title: title.trim(),
        text: text.trim(),
        category,
        photo_url: photoUrl.trim() || undefined,
      });

      navigate(ROUTES.FEED);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Не удалось создать публикацию');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="py-8 px-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">
          Новая история
        </h1>
        <p className="text-gray-600 text-lg">
          Поделитесь опытом с сообществом
        </p>
      </div>

      {/* Helper Card */}
      <div className="bg-velo-green-50 border border-velo-green-100 rounded-2xl p-6 mb-8">
        <h3 className="font-bold text-gray-900 mb-3">О чём написать?</h3>
        <p className="text-gray-700 text-sm leading-relaxed mb-3">
          Расскажите о маршруте, ремонте, новом велосипеде или полезном трюке. 
          Личный опыт помогает всему сообществу.
        </p>
        <ul className="text-sm text-gray-600 space-y-1">
          <li>• Будьте конкретны и делитесь деталями</li>
          <li>• Добавьте фотографии для наглядности</li>
          <li>• Выберите подходящую категорию</li>
        </ul>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="bg-white rounded-2xl shadow-sm p-8">
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6 text-sm">
            {error}
          </div>
        )}

        <div className="space-y-6">
          {/* Title */}
          <div>
            <Input
              label="Заголовок *"
              placeholder="Выходные на двух колёсах"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              disabled={isSubmitting}
              maxLength={MAX_POST_TITLE_LENGTH}
            />
            <p className="text-xs text-gray-500 mt-1">
              {title.length} / {MAX_POST_TITLE_LENGTH}
            </p>
          </div>

          {/* Category */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-3">
              Категория *
            </label>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {POST_CATEGORIES.map((cat) => (
                <button
                  key={cat}
                  type="button"
                  onClick={() => setCategory(cat)}
                  className={`px-4 py-3 rounded-xl font-semibold transition-all ${
                    category === cat
                      ? 'bg-velo-green text-white shadow-sm'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                  disabled={isSubmitting}
                >
                  {CATEGORY_LABELS[cat]}
                </button>
              ))}
            </div>
          </div>

          {/* Text */}
          <div>
            <Textarea
              label="Текст публикации *"
              placeholder="Утренний туман, лесные тропы и 42 километра свободы. Делюсь любимым маршрутом по Жигулям."
              value={text}
              onChange={(e) => setText(e.target.value)}
              disabled={isSubmitting}
              rows={10}
              maxLength={MAX_POST_TEXT_LENGTH}
            />
            <p className="text-xs text-gray-500 mt-1">
              {text.length} / {MAX_POST_TEXT_LENGTH}
            </p>
          </div>

          {/* Photo URL (Optional) */}
          <div>
            <h3 className="text-sm font-semibold text-gray-700 mb-3">
              + Добавьте одну фотографию
            </h3>
            <p className="text-sm text-gray-500 mb-3">
              Выберите файл с устройства
            </p>
            <Input
              placeholder="https://example.com/photo.jpg (или оставьте пустым)"
              value={photoUrl}
              onChange={(e) => setPhotoUrl(e.target.value)}
              disabled={isSubmitting}
            />
            <button
              type="button"
              className="mt-3 px-5 py-2.5 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg font-semibold transition-colors"
              disabled={isSubmitting}
            >
              Выбрать фотографию
            </button>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-4 mt-8 pt-6 border-t border-gray-200">
          <Button
            type="submit"
            variant="primary"
            isLoading={isSubmitting}
            className="flex-1"
          >
            Опубликовать
          </Button>
          <Button
            type="button"
            variant="secondary"
            onClick={() => navigate(ROUTES.FEED)}
            disabled={isSubmitting}
          >
            Отмена
          </Button>
        </div>
      </form>
    </div>
  );
};

export default CreatePostPage;
