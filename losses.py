import torch
import torch.nn.functional as F
from einops import rearrange, repeat


def reconstruction_loss_mse(x, f):
    """
    Reconstruction loss
    :param x: ``Tensor([C, H, W])``, real image
    :param f: ``Tensor([C, H, W])``, decoded image
    :return: ``float``, divergence between decoded and real images
    """
    return F.mse_loss(x, f)


def hinge_loss(real, fake):
    """
    The hinge version loss
    :param real: ``Tensor([1, 5, 5])``
    :param fake: ``Tensor([1, 5, 5])``
    :return: ``float``, loss
    """
    return (F.relu(1 + real) + F.relu(1 - fake)).mean()


def hinge_adv_loss(real_fake_logits_real, real_fake_logits_fake, device):
    """
    the hinge version of the adversarial loss
    :param real_fake_logits_real: ``Tensor([1, 5, 5])``
    :param real_fake_logits_fake: ``Tensor([1, 5, 5])``
    :param device: torch device
    :return: ``float``, discriminator loss
    """
    threshold = torch.Tensor([0.0]).to(device)
    real_loss = -1 * torch.mean(torch.minimum(threshold, -1 + real_fake_logits_real))
    fake_loss = -1 * torch.mean(torch.minimum(threshold, -1 - real_fake_logits_fake))
    return real_loss + fake_loss


def dual_contrastive_loss(real_logits, fake_logits, device):
    real_logits, fake_logits = map(lambda t: rearrange(t, '... -> (...)'), (real_logits, fake_logits))

    def loss_half(t1, t2):
        t1 = rearrange(t1, 'i -> i ()')
        t2 = repeat(t2, 'j -> i j', i=t1.shape[0])
        t = torch.cat((t1, t2), dim=-1)
        return F.cross_entropy(t, torch.zeros(t1.shape[0], device=device, dtype=torch.long))

    return loss_half(real_logits, fake_logits) + loss_half(-fake_logits, -real_logits)
