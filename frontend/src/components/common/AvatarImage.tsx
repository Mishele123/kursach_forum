import { useState } from 'react';
import { getUserInitials } from '../../utils/helpers';

export default function AvatarImage({ username, url }: { username: string; url?: string | null }) {
  const [failedUrl, setFailedUrl] = useState<string | null>(null);
  return url && url !== failedUrl
    ? <img className="avatar-image" src={url} alt={`Аватар ${username}`} onError={() => setFailedUrl(url)} />
    : <>{getUserInitials(username)}</>;
}
