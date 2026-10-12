from datetime import timedelta
from decimal import Decimal, InvalidOperation

from django.db.models import Q
from django.utils import timezone
from rest_framework import generics, serializers
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny

from .models import Job


class PublicJobSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    company = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    posted_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Job
        fields = [
            'id', 'slug', 'title', 'description', 'responsibilities',
            'required_skills', 'qualifications', 'category', 'company',
            'image', 'location', 'employment_type', 'work_mode',
            'experience_requirements', 'min_experience_years',
            'max_experience_years', 'min_salary', 'max_salary',
            'salary_period', 'application_deadline', 'posted_at',
            'application_method', 'application_email', 'application_url',
            'is_featured',
        ]

    def get_category(self, job):
        if job.category_id is None:
            return None
        return {'name': job.category.name, 'slug': job.category.slug}

    def get_company(self, job):
        if job.company_id is None:
            return {'name': job.company_display_name, 'logo': None}
        logo_url = job.company.logo.url if job.company.logo else None
        request = self.context.get('request')
        if logo_url and request:
            logo_url = request.build_absolute_uri(logo_url)
        return {'name': job.company.name, 'logo': logo_url}

    def get_image(self, job):
        if not job.image:
            return None
        image_url = job.image.url
        request = self.context.get('request')
        return request.build_absolute_uri(image_url) if request else image_url


class PublicJobQuerysetMixin:
    permission_classes = [AllowAny]
    serializer_class = PublicJobSerializer

    def get_queryset(self):
        queryset = Job.objects.open().filter(
            Q(category__isnull=True) | Q(category__active=True)
        ).select_related('category', 'company')
        params = self.request.query_params

        keyword = params.get('q', '').strip()
        if keyword:
            queryset = queryset.filter(
                Q(title__icontains=keyword)
                | Q(description__icontains=keyword)
                | Q(required_skills__icontains=keyword)
                | Q(responsibilities__icontains=keyword)
                | Q(employer_name__icontains=keyword)
                | Q(company__name__icontains=keyword)
            )

        for parameter, field in (
            ('category', 'category__slug'),
            ('location', 'location__icontains'),
        ):
            value = params.get(parameter, '').strip()
            if value:
                queryset = queryset.filter(**{field: value})

        employment_type = params.get('employment_type', params.get('type', '')).strip()
        if employment_type:
            queryset = queryset.filter(employment_type=employment_type)

        experience = params.get('experience', '').strip()
        if experience:
            queryset = queryset.filter(experience_requirements=experience)

        work_mode = params.get('work_mode', '').strip()
        if work_mode:
            if work_mode not in Job.WorkMode.values:
                raise ValidationError({'work_mode': 'Select a valid work mode.'})
            queryset = queryset.filter(work_mode=work_mode)

        for parameter, lookup, null_lookup in (
            ('min_experience', 'max_experience_years__gte', 'max_experience_years__isnull'),
            ('max_experience', 'min_experience_years__lte', 'min_experience_years__isnull'),
        ):
            raw_value = params.get(parameter, '').strip()
            if raw_value:
                try:
                    years = Decimal(raw_value)
                except InvalidOperation:
                    raise ValidationError({parameter: 'Enter a valid non-negative number of years.'})
                if not years.is_finite() or years < 0:
                    raise ValidationError({parameter: 'Enter a valid non-negative number of years.'})
                queryset = queryset.filter(
                    Q(**{lookup: years}) | Q(**{null_lookup: True})
                )

        for parameter, lookup in (
            ('min_salary', 'max_salary__gte'),
            ('max_salary', 'min_salary__lte'),
        ):
            raw_value = params.get(parameter, '').strip()
            if raw_value:
                try:
                    amount = Decimal(raw_value)
                except InvalidOperation:
                    raise ValidationError({parameter: 'Enter a valid non-negative amount.'})
                if not amount.is_finite() or amount < 0:
                    raise ValidationError({parameter: 'Enter a valid non-negative amount.'})
                queryset = queryset.filter(**{lookup: amount})

        date_posted = params.get('date_posted', '').strip()
        posted_ranges = {'24h': 1, '7d': 7, '30d': 30}
        if date_posted:
            if date_posted not in posted_ranges:
                raise ValidationError({'date_posted': 'Select 24h, 7d, or 30d.'})
            cutoff = timezone.now() - timedelta(days=posted_ranges[date_posted])
            queryset = queryset.filter(
                Q(published_at__gte=cutoff)
                | Q(published_at__isnull=True, created_at__gte=cutoff)
            )

        if params.get('sort') == 'oldest':
            return queryset.order_by('published_at', 'created_at')
        return queryset.order_by('-published_at', '-created_at')


class PublicJobListAPIView(PublicJobQuerysetMixin, generics.ListAPIView):
    pass


class PublicJobDetailAPIView(PublicJobQuerysetMixin, generics.RetrieveAPIView):
    lookup_field = 'slug'
