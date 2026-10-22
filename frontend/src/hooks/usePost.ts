import { useState, useEffect } from 'react';
import { postsApi } from '../services/api';
import type { Post } from '../types';

export const usePost = (postId: number) => {
  const [post, setPost] = useState<Post | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPost = async () => {
      try {
        setIsLoading(true);
        const data = await postsApi.getPost(postId);
        setPost(data);
        setError(null);
      } catch (err) {
        setError('Не удалось загрузить публикацию');
        console.error('Failed to fetch post:', err);
      } finally {
        setIsLoading(false);
      }
    };

    if (Number.isInteger(postId) && postId > 0) {
      fetchPost();
    } else {
      setError("Публикация не найдена");
      setIsLoading(false);
    }
  }, [postId]);

  return { post, isLoading, error };
};
