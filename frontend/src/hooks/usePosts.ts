import { useState, useEffect } from 'react';
import { postsApi } from '../services/api';
import type { Post, CreatePostDto } from '../types';

export const usePosts = (limit: number = 20, offset: number = 0) => {
  const [posts, setPosts] = useState<Post[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchPosts = async () => {
    try {
      setIsLoading(true);
      const data = await postsApi.getPosts(limit, offset);
      setPosts(data);
      setError(null);
    } catch (err) {
      setError('Не удалось загрузить публикации');
      console.error('Failed to fetch posts:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchPosts();
  }, [limit, offset]);

  const createPost = async (postData: CreatePostDto): Promise<Post | null> => {
    try {
      const newPost = await postsApi.createPost(postData);
      setPosts((prev) => [newPost, ...prev]);
      return newPost;
    } catch (err) {
      console.error('Failed to create post:', err);
      throw err;
    }
  };

  return {
    posts,
    isLoading,
    error,
    refetch: fetchPosts,
    createPost,
  };
};

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

    if (postId) {
      fetchPost();
    }
  }, [postId]);

  return { post, isLoading, error };
};
