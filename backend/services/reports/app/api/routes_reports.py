from fastapi import APIRouter

router = APIRouter()

async def get_report_service(db=Depends(get_db), redis=Depends(get_redis)):
    return ReportService(db=db, redis_client=redis)


@router.get("/")
async def get_reports():

@router.post()

@router.delete()

